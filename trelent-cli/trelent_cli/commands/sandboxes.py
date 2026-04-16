"""Sandbox management commands."""
import subprocess
import sys
from pathlib import Path

import click

from ..client import get_client, load_profile, get_profile, DEFAULT_REGISTRY_URL


@click.group("sandboxes")
def sandboxes():
    """Manage sandboxes."""
    pass


@sandboxes.command("build")
@click.argument("path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("-t", "--tag", "image_tag", help="Image name and tag (e.g. my-agent:v1). Defaults to <folder>:latest")
def build_sandbox(path: str, image_tag: str | None):
    """Build and push a sandbox image to the registry.

    PATH is the directory containing the Dockerfile.

    Examples:

        trelent sandboxes build ./agents/translator-agent

        trelent sandboxes build -t my-agent:v2 ./agents/translator-agent
    """
    build_path = Path(path)
    profile_name = get_profile()
    profile = load_profile(profile_name)

    if not profile.client_id or not profile.client_secret:
        click.echo(f"Error: Missing credentials for profile '{profile_name}'.", err=True)
        click.echo("Run 'trelent auth add' first.", err=True)
        sys.exit(1)

    registry = (profile.registry_url or DEFAULT_REGISTRY_URL).removeprefix("https://").removeprefix("http://")

    if image_tag:
        name_tag = image_tag if ":" in image_tag else f"{image_tag}:latest"
    else:
        name_tag = f"{build_path.name}:latest"

    full_image = f"{registry}/{profile.client_id}/{name_tag}"

    click.echo(f"Building {full_image} from {build_path}")

    if _docker_login(registry, profile.client_id, profile.client_secret) != 0:
        sys.exit(1)

    if _docker_build(full_image, build_path) != 0:
        sys.exit(1)

    if _docker_push(full_image) != 0:
        sys.exit(1)

    click.echo(f"Successfully pushed {full_image}")


def _docker_login(registry: str, username: str, password: str) -> int:
    """Login to Docker registry. Returns exit code."""
    result = subprocess.run(
        ["docker", "login", registry, "-u", username, "--password-stdin"],
        input=password.encode(),
        capture_output=True,
    )
    if result.returncode != 0:
        click.echo(f"Docker login failed: {result.stderr.decode()}", err=True)
    return result.returncode


def _docker_build(image: str, path: Path) -> int:
    """Build Docker image. Returns exit code."""
    result = subprocess.run(
        ["docker", "build", "-t", image, str(path)],
        capture_output=False,
    )
    if result.returncode != 0:
        click.echo("Docker build failed.", err=True)
    return result.returncode


def _docker_push(image: str) -> int:
    """Push Docker image. Returns exit code."""
    result = subprocess.run(
        ["docker", "push", image],
        capture_output=False,
    )
    if result.returncode != 0:
        click.echo("Docker push failed.", err=True)
    return result.returncode


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
