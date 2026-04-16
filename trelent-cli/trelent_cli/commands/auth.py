"""Authentication commands."""
import click
import requests
from ..client import (
    save_profile, load_profile, delete_profile, check_credentials,
    list_profiles, get_default_profile, set_default_profile, get_profile,
    PROFILES_DIR, DEFAULT_API_URL, DEFAULT_REGISTRY_URL,
)


@click.group("auth")
def auth():
    """Manage authentication profiles."""
    pass


@auth.command("add")
@click.argument("profile", required=False)
@click.option("--id", "client_id", help="Client ID")
@click.option("--secret", "client_secret", help="Client secret")
@click.option("--api-url", help="API URL")
@click.option("--registry-url", help="Docker registry URL for agent images")
@click.option("--skip-verify", is_flag=True, help="Skip credential verification")
def add(
    profile: str | None,
    client_id: str | None,
    client_secret: str | None,
    api_url: str | None,
    registry_url: str | None,
    skip_verify: bool,
):
    """Add a new profile.

    Examples:
      trelent auth add dev
      trelent auth add prod --id YOUR_ID --secret YOUR_SECRET
    """
    if not profile:
        profile = click.prompt("Profile name")

    existing = load_profile(profile)

    if not client_id:
        default_id = existing.client_id or ""
        client_id = click.prompt("Client ID", default=default_id or None)
    if not client_secret:
        client_secret = click.prompt("Client secret")
    if not api_url:
        default_url = existing.api_url or DEFAULT_API_URL
        api_url = click.prompt("API URL", default=default_url)
    if not registry_url:
        default_registry = existing.registry_url or DEFAULT_REGISTRY_URL
        registry_url = click.prompt("Registry URL", default=default_registry)

    if not skip_verify:
        click.echo("Verifying credentials...")
        ok, msg = check_credentials(client_id, client_secret, api_url)
        if not ok:
            click.echo(f"✗ {msg}", err=True)
            raise SystemExit(1)
        click.echo(f"✓ {msg}")

    save_profile(profile, client_id, client_secret, api_url, registry_url)
    click.echo(f"Profile '{profile}' saved to {PROFILES_DIR / profile}")


@auth.command("list")
def list_cmd():
    """List all profiles."""
    profiles = list_profiles()
    default = get_default_profile()
    current = get_profile()

    if not profiles:
        click.echo("No profiles configured. Run 'trelent auth add <name>'.")
        return

    for p in profiles:
        markers = []
        if p == default:
            markers.append("default")
        if p == current:
            markers.append("active")
        suffix = f" ({', '.join(markers)})" if markers else ""
        click.echo(f"  {p}{suffix}")


@auth.command("use")
@click.argument("profile")
def use(profile: str):
    """Set the default profile.

    Example: trelent auth use dev
    """
    try:
        set_default_profile(profile)
        click.echo(f"Now using profile '{profile}'")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@auth.command("test")
def test():
    """Test the current profile's credentials."""
    profile = get_profile()
    config = load_profile(profile)

    if not config.client_id or not config.client_secret:
        click.echo(f"No credentials for profile '{profile}'. Run 'trelent auth add {profile}'.", err=True)
        raise SystemExit(1)

    click.echo(f"Testing '{profile}'...")
    ok, msg = check_credentials(config.client_id, config.client_secret, config.api_url)

    if ok:
        click.echo(f"✓ {msg}")
    else:
        click.echo(f"✗ {msg}", err=True)
        raise SystemExit(1)


@auth.command("show")
def show():
    """Show current profile details."""
    profile = get_profile()
    config = load_profile(profile)

    if not config.client_id:
        click.echo(f"Profile '{profile}' not configured.")
        return

    click.echo(f"Profile:      {profile}")
    click.echo(f"API URL:      {config.api_url or DEFAULT_API_URL}")
    click.echo(f"Registry URL: {config.registry_url or DEFAULT_REGISTRY_URL}")
    click.echo(f"Client ID:    {config.client_id}")
    click.echo(f"Secret:       {'*' * 8}")


@auth.command("rm")
@click.argument("profile")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def rm(profile: str, yes: bool):
    """Remove a profile.

    Example: trelent auth rm dev
    """
    if not yes:
        click.confirm(f"Delete profile '{profile}'?", abort=True)

    try:
        delete_profile(profile)
        click.echo(f"Deleted profile '{profile}'")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@auth.command("debug")
def debug():
    """Debug token exchange for current profile."""
    profile = get_profile()
    config = load_profile(profile)

    if not config.client_id:
        click.echo(f"No credentials for profile '{profile}'")
        return

    url = config.api_url or DEFAULT_API_URL
    token_url = f"{url.rstrip('/')}/token"

    click.echo(f"Profile: {profile}")
    click.echo(f"Token URL: {token_url}")
    click.echo()

    resp = requests.post(
        token_url,
        json={
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "scope": "AgentOrchestrator:*",
        },
    )

    click.echo(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        click.echo("Token: " + resp.json().get("access_token", "")[:50] + "...")
    else:
        click.echo(f"Error: {resp.text[:200]}")
