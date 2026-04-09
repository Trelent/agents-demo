"""Sandbox management commands."""
import click
from ..client import get_client


@click.group("sandboxes")
def sandboxes():
    """Manage sandboxes."""
    pass


@sandboxes.command("list")
def list_sandboxes():
    """List available sandboxes."""
    client = get_client()
    sandbox_list = client.images.list()

    if not sandbox_list:
        click.echo("No sandboxes found.")
        return

    click.echo("Available sandboxes:")
    for sb in sandbox_list:
        click.echo(f"  - {sb}")


@sandboxes.command("get")
@click.argument("name")
def get_sandbox(name: str):
    """Get details of a specific sandbox.

    Example: trelent sandboxes get translator:latest
    """
    client = get_client()
    sandbox = client.images.get(name)

    click.echo(f"Name:    {sandbox.name}")
    click.echo(f"Image:   {sandbox.image}")
    click.echo(f"Status:  {sandbox.status}")
