"""Main CLI entry point."""
import click

from .client import set_profile
from .commands import auth, runs, sandboxes


@click.group()
@click.option("--profile", "-p", envvar="TRELENT_PROFILE", help="Use a specific profile")
@click.version_option(version="0.1.0")
@click.pass_context
def main(ctx, profile: str | None):
    """CLI wrapper for trelent-agents SDK."""
    if profile:
        set_profile(profile)


main.add_command(auth)
main.add_command(runs)
main.add_command(runs, name="run")
main.add_command(runs, name="r")
main.add_command(sandboxes)
main.add_command(sandboxes, name="sandbox")
main.add_command(sandboxes, name="sbx")
main.add_command(sandboxes, name="s")


if __name__ == "__main__":
    main()
