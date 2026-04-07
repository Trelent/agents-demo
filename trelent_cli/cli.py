"""Main CLI entry point."""
import click
from dotenv import load_dotenv

from .commands import auth, runs, sandboxes

load_dotenv()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """CLI wrapper for trelent-agents SDK."""
    pass


main.add_command(auth)
main.add_command(runs)
main.add_command(sandboxes)


if __name__ == "__main__":
    main()
