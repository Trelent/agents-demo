"""Run management commands."""
import os
import time
import click
from trelent_agents import ClaudeCodeHarnessSpec, HarnessKind, LocalImporter
from trelent_agents.types import HarnessSpec
from ..client import get_client


def _get_latest_run_id(client) -> str:
    """Get the most recent run ID or exit."""
    run_list = client.runs.list()
    if not run_list:
        click.echo("No runs found.", err=True)
        raise SystemExit(1)
    return run_list[0].id


def _poll_until_complete(client, run_id: str, poll_interval: int = 2):
    """Poll a run until it reaches a terminal state."""
    while True:
        run = client.runs.get(run_id)
        click.echo(f"Status: {run.status}")

        if run.status in ("completed", "failed", "cancelled"):
            return run

        time.sleep(poll_interval)


@click.group("runs")
def runs():
    """Manage runs."""
    pass


@runs.command("list")
@click.option("--limit", "-n", default=10, help="Number of runs to show")
@click.option("--sandbox", "-s", help="Filter by sandbox name")
def list_runs(limit: int, sandbox: str | None):
    """List recent runs."""
    client = get_client()
    run_list = client.runs.list(sandbox=sandbox)[:limit]

    if not run_list:
        click.echo("No runs found.")
        return

    click.echo(f"{'ID':<20} {'Status':<12} {'Sandbox':<30}")
    click.echo("-" * 62)
    for run in run_list:
        click.echo(f"{run.id:<20} {run.status:<12} {run.sandbox:<30}")


@runs.command("get")
@click.argument("run_id", required=False)
@click.option("--latest", "-l", is_flag=True, help="Get the most recent run")
def get_run(run_id: str | None, latest: bool):
    """Get details of a specific run.

    Example: trelent runs get run-123abc
             trelent runs get --latest
    """
    client = get_client()

    if latest:
        run_id = _get_latest_run_id(client)

    if not run_id:
        click.echo("Error: Provide a run ID or use --latest", err=True)
        raise SystemExit(1)

    run = client.runs.get(run_id)

    click.echo(f"ID:      {run.id}")
    click.echo(f"Status:  {run.status}")
    click.echo(f"Sandbox: {run.sandbox}")
    click.echo(f"Model:   {run.harness.model}")

    if run.result:
        click.echo("\n--- Output ---")
        click.echo(run.result.output)


@runs.command("track")
@click.argument("run_id", required=False)
@click.option("--latest", "-l", is_flag=True, help="Track the most recent run")
@click.option("--poll", "-p", default=2, help="Poll interval in seconds")
def track_run(run_id: str | None, latest: bool, poll: int):
    """Track a run until completion.

    Example: trelent runs track run-123abc
             trelent runs track --latest
    """
    client = get_client()

    if latest:
        run_id = _get_latest_run_id(client)

    if not run_id:
        click.echo("Error: Provide a run ID or use --latest", err=True)
        raise SystemExit(1)

    click.echo(f"Tracking run: {run_id}")
    run = _poll_until_complete(client, run_id, poll)

    click.echo("\n--- Result ---")
    click.echo(run.result.output if run.result else "(no output)")


@runs.command("create")
@click.option("--sandbox", "-s", required=True, help="Sandbox name (e.g., translator:latest)")
@click.option("--prompt", "-p", required=True, help="Prompt for the run")
@click.option("--import-path", "-i", multiple=True, help="Local paths to import (mounted at /mnt/)")
@click.option("--track", "-t", "should_track", is_flag=True, help="Track run until completion")
def create_run(sandbox: str, prompt: str, import_path: tuple, should_track: bool):
    """Create a new run.

    Example: trelent runs create -s translator:latest -p "Translate hello to Spanish"
    """
    client = get_client()

    imports = [LocalImporter(path=p) for p in import_path] if import_path else None

    run = client.runs.create(
        sandbox=sandbox,
        harness=ClaudeCodeHarnessSpec(
            kind=HarnessKind.CLAUDE_CODE,
            model="claude-sonnet-4-6",
        ),
        prompt=prompt,
        imports=imports,
    )

    click.echo(f"Run ID: {run.id}")
    click.echo(f"Status: {run.status}")

    if imports:
        click.echo(f"\nImported {len(imports)} path(s) to /mnt/")

    if not should_track:
        return

    click.echo("\nTracking...")
    run = _poll_until_complete(client, run.id)

    click.echo("\n--- Result ---")
    click.echo(run.result.output if run.result else "(no output)")


@runs.command("fork")
@click.argument("parent_id", required=False)
@click.option("--latest", "-l", is_flag=True, help="Fork the most recent run")
@click.option("--prompt", "-p", required=True, help="New prompt for the forked run")
@click.option("--import-path", "-i", multiple=True, help="Local paths to import")
def fork_run(parent_id: str | None, latest: bool, prompt: str, import_path: tuple):
    """Fork an existing run with a new prompt.

    Example: trelent runs fork run-123abc -p "Now translate to French"
             trelent runs fork --latest -p "Now translate to French"
    """
    client = get_client()

    if latest:
        parent_id = _get_latest_run_id(client)

    if not parent_id:
        click.echo("Error: Provide a parent run ID or use --latest", err=True)
        raise SystemExit(1)

    parent_run = client.runs.get(parent_id)
    imports = [LocalImporter(path=p) for p in import_path] if import_path else None

    child_run = parent_run.fork(prompt=prompt, imports=imports)

    click.echo(f"Parent: {parent_id}")
    click.echo(f"Child:  {child_run.id}")
    click.echo(f"Status: {child_run.status}")
