"""Main CLI entry point."""
import click
from dotenv import load_dotenv

from .client import set_profile
from .commands import auth, runs, sandboxes

load_dotenv()


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
main.add_command(sandboxes)


if __name__ == "__main__":
    main()
