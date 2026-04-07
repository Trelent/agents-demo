"""Main CLI entry point."""
import time
import click
from dotenv import load_dotenv
from trelent_agents import LocalImporter
from .client import get_client, save_config, CONFIG_FILE

load_dotenv()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """CLI wrapper for trelent-agents SDK."""
    pass


# --- Auth ---

@main.command("auth")
@click.option("--id", "client_id", help="Client ID (non-interactive)")
@click.option("--secret", "client_secret", help="Client secret (non-interactive)")
@click.option("--api-url", help="API URL (default: https://agents.trelent.com)")
def auth(client_id: str | None, client_secret: str | None, api_url: str | None):
    """Configure authentication credentials.

    Credentials are stored in ~/.trelent/agents/config.json

    Interactive:  trelent auth
    Non-interactive:  trelent auth --id YOUR_ID --secret YOUR_SECRET
    """
    if not client_id:
        client_id = click.prompt("Client ID")
    if not client_secret:
        client_secret = click.prompt("Client secret", hide_input=True)

    save_config(client_id, client_secret, api_url)
    click.echo(f"Credentials saved to {CONFIG_FILE}")


# --- Runs ---

@main.command("runs")
@click.option("--limit", "-n", default=10, help="Number of runs to show")
@click.option("--sandbox", "-s", help="Filter by sandbox name")
def list_runs(limit: int, sandbox: str | None):
    """List recent runs."""
    client = get_client()
    runs = client.runs.list(sandbox=sandbox)[:limit]

    if not runs:
        click.echo("No runs found.")
        return

    click.echo(f"{'ID':<20} {'Status':<12} {'Sandbox':<30}")
    click.echo("-" * 62)
    for run in runs:
        click.echo(f"{run.id:<20} {run.status:<12} {run.sandbox:<30}")


@main.command("track")
@click.argument("run_id", required=False)
@click.option("--latest", "-l", is_flag=True, help="Track the most recent run")
@click.option("--poll", "-p", default=2, help="Poll interval in seconds")
def track_run(run_id: str | None, latest: bool, poll: int):
    """Track a run until completion.

    Usage: trelent track run-123abc
           trelent track --latest
    """
    client = get_client()

    if latest:
        runs = client.runs.list()
        if not runs:
            click.echo("No runs found.", err=True)
            raise SystemExit(1)
        run_id = runs[0].id

    if not run_id:
        click.echo("Error: Provide a run ID or use --latest", err=True)
        raise SystemExit(1)

    click.echo(f"Tracking run: {run_id}")

    while True:
        run = client.runs.get(run_id)
        click.echo(f"Status: {run.status}")

        if run.status in ("completed", "failed", "cancelled"):
            break

        time.sleep(poll)

    click.echo("\n--- Result ---")
    click.echo(run.result.output if run.result else "(no output)")


@main.command("get")
@click.argument("run_id", required=False)
@click.option("--latest", "-l", is_flag=True, help="Get the most recent run")
def get_run(run_id: str | None, latest: bool):
    """Get details of a specific run."""
    client = get_client()

    if latest:
        runs = client.runs.list()
        if not runs:
            click.echo("No runs found.", err=True)
            raise SystemExit(1)
        run_id = runs[0].id

    if not run_id:
        click.echo("Error: Provide a run ID or use --latest", err=True)
        raise SystemExit(1)

    run = client.runs.get(run_id)

    click.echo(f"ID:      {run.id}")
    click.echo(f"Status:  {run.status}")
    click.echo(f"Sandbox: {run.sandbox}")
    click.echo(f"Model:   {run.model}")

    if run.result:
        click.echo("\n--- Output ---")
        click.echo(run.result.output)


# --- Create ---

@main.command("create")
@click.option("--sandbox", "-s", required=True, help="Sandbox name (e.g., translator:latest)")
@click.option("--model", "-m", default="claude-sonnet-4-5", help="Model to use")
@click.option("--prompt", "-p", required=True, help="Prompt for the run")
@click.option("--import-path", "-i", multiple=True, help="Local paths to import (mounted at /mnt/)")
@click.option("--track", "-t", is_flag=True, help="Track run until completion")
def create_run(sandbox: str, model: str, prompt: str, import_path: tuple, track: bool):
    """Create a new run.

    Example: trelent create -s translator:latest -p "Translate hello to Spanish"
    """
    client = get_client()

    imports = [LocalImporter(path=p) for p in import_path] if import_path else None

    run = client.runs.create(
        sandbox=sandbox,
        model=model,
        prompt=prompt,
        imports=imports,
    )

    click.echo(f"Run ID: {run.id}")
    click.echo(f"Status: {run.status}")

    if imports:
        click.echo(f"\nImported {len(imports)} path(s) to /mnt/")

    if not track:
        return

    click.echo("\nTracking...")
    while True:
        run = client.runs.get(run.id)
        click.echo(f"Status: {run.status}")

        if run.status in ("completed", "failed", "cancelled"):
            break

        time.sleep(2)

    click.echo("\n--- Result ---")
    click.echo(run.result.output if run.result else "(no output)")


# --- Fork ---

@main.command("fork")
@click.argument("parent_id", required=False)
@click.option("--latest", "-l", is_flag=True, help="Fork the most recent run")
@click.option("--prompt", "-p", required=True, help="New prompt for the forked run")
@click.option("--import-path", "-i", multiple=True, help="Local paths to import")
def fork_run(parent_id: str | None, latest: bool, prompt: str, import_path: tuple):
    """Fork an existing run with a new prompt.

    Example: trelent fork run-123abc -p "Now translate to French"
             trelent fork --latest -p "Now translate to French"
    """
    client = get_client()

    if latest:
        runs = client.runs.list()
        if not runs:
            click.echo("No runs found.", err=True)
            raise SystemExit(1)
        parent_id = runs[0].id

    if not parent_id:
        click.echo("Error: Provide a parent run ID or use --latest", err=True)
        raise SystemExit(1)

    parent_run = client.runs.get(parent_id)
    imports = [LocalImporter(path=p) for p in import_path] if import_path else None

    child_run = parent_run.fork(prompt=prompt, imports=imports)

    click.echo(f"Parent: {parent_id}")
    click.echo(f"Child:  {child_run.id}")
    click.echo(f"Status: {child_run.status}")


# --- Sandboxes ---

@main.group("sandboxes")
def sandboxes():
    """Manage sandboxes."""
    pass


@sandboxes.command("list")
def list_sandboxes():
    """List available sandboxes."""
    client = get_client()
    sandbox_list = client.sandboxes.list()

    if not sandbox_list:
        click.echo("No sandboxes found.")
        return

    click.echo("Available sandboxes:")
    for sb in sandbox_list:
        click.echo(f"  - {sb}")


@sandboxes.command("register")
@click.argument("name")
def register_sandbox(name: str):
    """Register a new sandbox.

    Example: trelent sandboxes register translator:latest
    """
    client = get_client()
    click.echo(f"Registering sandbox: {name}")
    client.sandboxes.register(name)
    click.echo("Done.")


if __name__ == "__main__":
    main()
