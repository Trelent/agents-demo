"""Client initialization and config management."""
import os
import sys
from pathlib import Path
import requests
from trelent_agents import Client

CONFIG_DIR = Path.home() / ".trelent"
PROFILES_DIR = CONFIG_DIR / "profiles"
ACTIVE_FILE = CONFIG_DIR / "active"
DEFAULT_API_URL = "https://agents.trelent.com"
DEFAULT_PROFILE = "default"

_current_profile: str | None = None


def set_profile(profile: str) -> None:
    """Set the current profile for this session."""
    global _current_profile
    _current_profile = profile


def get_profile() -> str:
    """Get the current profile name."""
    if _current_profile:
        return _current_profile
    if os.environ.get("TRELENT_PROFILE"):
        return os.environ["TRELENT_PROFILE"]
    return get_default_profile()


def get_default_profile() -> str:
    """Get the default profile name from ~/.trelent/active."""
    if ACTIVE_FILE.exists():
        return ACTIVE_FILE.read_text().strip()
    return DEFAULT_PROFILE


def set_default_profile(profile: str) -> None:
    """Set the default profile."""
    profile_file = PROFILES_DIR / profile
    if not profile_file.exists():
        raise ValueError(f"Profile '{profile}' does not exist")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_FILE.write_text(profile + "\n")


def list_profiles() -> list[str]:
    """List all available profile names."""
    if not PROFILES_DIR.exists():
        return []
    return [f.name for f in PROFILES_DIR.iterdir() if f.is_file()]


def load_profile(profile: str | None = None) -> dict:
    """Load a specific profile's config."""
    profile = profile or get_profile()
    profile_file = PROFILES_DIR / profile

    if not profile_file.exists():
        return {}

    data = {}
    for line in profile_file.read_text().splitlines():
        line = line.strip()
        if line and "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()

    return data


def save_profile(profile: str, client_id: str, client_secret: str, api_url: str | None = None) -> None:
    """Save credentials to a profile."""
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profile_file = PROFILES_DIR / profile

    lines = [
        f"client_id={client_id}",
        f"client_secret={client_secret}",
    ]
    if api_url:
        lines.append(f"api_url={api_url}")

    profile_file.write_text("\n".join(lines) + "\n")
    profile_file.chmod(0o600)

    # Set as default if it's the first profile
    if not ACTIVE_FILE.exists():
        ACTIVE_FILE.write_text(profile + "\n")


def delete_profile(profile: str) -> None:
    """Delete a profile."""
    profile_file = PROFILES_DIR / profile

    if not profile_file.exists():
        raise ValueError(f"Profile '{profile}' does not exist")

    profile_file.unlink()

    # If we deleted the active profile, clear it
    if ACTIVE_FILE.exists() and ACTIVE_FILE.read_text().strip() == profile:
        ACTIVE_FILE.unlink()


def check_credentials(client_id: str, client_secret: str, api_url: str | None = None) -> tuple[bool, str]:
    """Check if credentials are valid by requesting a token."""
    url = api_url or DEFAULT_API_URL
    token_url = f"{url.rstrip('/')}/token"

    try:
        resp = requests.post(
            token_url,
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "AgentOrchestrator:*",
            },
        )

        if resp.status_code == 200:
            return True, f"Connected to {url}"

        return False, f"Auth failed ({resp.status_code}): {resp.text}"
    except requests.RequestException as e:
        return False, f"Connection error: {e}"


def get_client() -> Client:
    """Create an authenticated client from env vars or config file."""
    client_id = os.environ.get("TRELENT_CLIENT_ID")
    client_secret = os.environ.get("TRELENT_CLIENT_SECRET")
    api_url = os.environ.get("TRELENT_API_URL")

    if not client_id or not client_secret:
        profile_config = load_profile()
        client_id = client_id or profile_config.get("client_id")
        client_secret = client_secret or profile_config.get("client_secret")
        api_url = api_url or profile_config.get("api_url")

    if not client_id or not client_secret:
        profile = get_profile()
        print(f"Error: Missing credentials for profile '{profile}'.", file=sys.stderr)
        print("Run 'trelent auth add' or set TRELENT_CLIENT_ID and TRELENT_CLIENT_SECRET.", file=sys.stderr)
        sys.exit(1)

    return Client(
        api_url=api_url or DEFAULT_API_URL,
        client_id=client_id,
        client_secret=client_secret,
    )
