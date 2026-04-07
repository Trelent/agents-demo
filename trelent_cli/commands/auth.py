"""Authentication commands."""
import click
from ..client import save_config, load_config, check_credentials, CONFIG_FILE, DEFAULT_API_URL


@click.group("auth")
def auth():
    """Manage authentication."""
    pass


@auth.command("login")
@click.option("--id", "client_id", help="Client ID (non-interactive)")
@click.option("--secret", "client_secret", help="Client secret (non-interactive)")
@click.option("--api-url", help="API URL (non-interactive)")
def login(client_id: str | None, client_secret: str | None, api_url: str | None):
    """Configure authentication credentials.

    Interactive:  trelent auth login
    Non-interactive:  trelent auth login --id YOUR_ID --secret YOUR_SECRET
    """
    if not client_id:
        client_id = click.prompt("Client ID")
    if not client_secret:
        client_secret = click.prompt("Client secret", hide_input=True)
    if not api_url:
        api_url = click.prompt("API URL", default=DEFAULT_API_URL)

    click.echo("Verifying credentials...")
    ok, msg = check_credentials(client_id, client_secret, api_url)

    if not ok:
        click.echo(f"✗ {msg}", err=True)
        raise SystemExit(1)

    save_config(client_id, client_secret, api_url)
    click.echo(f"✓ {msg}")
    click.echo(f"Credentials saved to {CONFIG_FILE}")


@auth.command("test")
def test():
    """Test the current authentication credentials."""
    config = load_config()

    if not config.get("client_id") or not config.get("client_secret"):
        click.echo(f"No credentials found. Run 'trelent auth login' first.", err=True)
        raise SystemExit(1)

    click.echo(f"Testing credentials from {CONFIG_FILE}...")
    ok, msg = check_credentials(
        config["client_id"],
        config["client_secret"],
        config.get("api_url"),
    )

    if ok:
        click.echo(f"✓ {msg}")
    else:
        click.echo(f"✗ {msg}", err=True)
        raise SystemExit(1)


@auth.command("status")
def status():
    """Show current authentication status."""
    config = load_config()

    if not config:
        click.echo("Not authenticated. Run 'trelent auth login'.")
        return

    click.echo(f"Config: {CONFIG_FILE}")
    click.echo(f"API URL: {config.get('api_url', DEFAULT_API_URL)}")
    click.echo(f"Client ID: {config.get('client_id', '(not set)')}")
    click.echo(f"Client Secret: {'*' * 10 if config.get('client_secret') else '(not set)'}")
