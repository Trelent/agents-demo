"""Run management commands."""
import time
import click
from trelent_agents import (
    ClaudeCodeHarnessSpec,
    CodexHarnessSpec,
    GeminiHarnessSpec,
    LocalImporter,
)
from trelent_agents.types import HarnessSpec
from ..client import get_client


HARNESS_ALIASES = {
    "claude": ClaudeCodeHarnessSpec,
    "claude_code": ClaudeCodeHarnessSpec,
    "claude-code": ClaudeCodeHarnessSpec,
    "codex": CodexHarnessSpec,
    "gpt": CodexHarnessSpec,
    "gemini": GeminiHarnessSpec,
}


def _infer_harness_from_model(model: str) -> type[HarnessSpec] | None:
    """Guess harness class from model name prefix."""
    prefix = model.lower()
    if prefix.startswith("claude"):
        return ClaudeCodeHarnessSpec
    if prefix.startswith("gpt") or prefix.startswith("codex") or prefix.startswith("o"):
        return CodexHarnessSpec
    if prefix.startswith("gemini"):
        return GeminiHarnessSpec
    return None


def _build_harness(harness: str | None, model: str | None) -> HarnessSpec | None:
    """Construct a harness spec from CLI flags.

    - No flags: returns None (SDK default = claude_code)
    - --harness only: uses harness's default model
    - --model only: infers harness from model prefix
    - Both: uses specified harness + model
    """
    if not harness and not model:
        return None

    if harness:
        key = harness.lower()
        if key not in HARNESS_ALIASES:
            valid = ", ".join(sorted(set(HARNESS_ALIASES.keys())))
            raise click.BadParameter(f"Unknown harness '{harness}'. Valid: {valid}")
        cls = HARNESS_ALIASES[key]
    else:
        cls = _infer_harness_from_model(model or "")
        if cls is None:
            raise click.BadParameter(
                f"Could not infer harness from model '{model}'. Use -h to specify (claude, codex, gemini)."
            )

    return cls(model=model) if model else cls()


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
    click.echo(f"Harness: {run.harness.kind} ({run.harness.model})")

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
@click.option("--harness", "-h", help="Harness: claude, codex, or gemini (default: claude)")
@click.option("--model", "-m", help="Model override (auto-infers harness from prefix if -h omitted)")
@click.option("--import-path", "-i", multiple=True, help="Local paths to import (mounted at /mnt/)")
@click.option("--track", "-t", "should_track", is_flag=True, help="Track run until completion")
def create_run(
    sandbox: str,
    prompt: str,
    harness: str | None,
    model: str | None,
    import_path: tuple,
    should_track: bool,
):
    """Create a new run.

    Examples:

        trelent runs create -s translator:latest -p "Translate hello"

        trelent runs create -s my-agent:latest -p "Do it" -h codex

        trelent runs create -s my-agent:latest -p "Do it" -m gpt-5.4

        trelent runs create -s my-agent:latest -p "Do it" -h gemini -m gemini-3.1-pro
    """
    client = get_client()
    harness_spec = _build_harness(harness, model)
    imports = [LocalImporter(path=p) for p in import_path] if import_path else None

    run = client.runs.create(
        sandbox=sandbox,
        harness=harness_spec,
        prompt=prompt,
        imports=imports,
    )

    click.echo(f"Run ID:  {run.id}")
    click.echo(f"Status:  {run.status}")
    click.echo(f"Harness: {run.harness.kind} ({run.harness.model})")

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
