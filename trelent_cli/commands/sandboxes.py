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
    sandbox_list = client.sandboxes.list()

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
    sandbox = client.sandboxes.get(name)

    click.echo(f"Name:    {sandbox.name}")
    click.echo(f"Image:   {sandbox.image}")
    click.echo(f"Status:  {sandbox.status}")


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
