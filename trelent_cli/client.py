"""Client initialization and config management."""
import json
import os
import sys
from pathlib import Path
from trelent_agents import Client

CONFIG_DIR = Path.home() / ".trelent" / "agents"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_API_URL = "https://agents.trelent.com"


def load_config() -> dict:
    """Load config from ~/.trelent/agents/config.json."""
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def save_config(client_id: str, client_secret: str, api_url: str | None = None) -> None:
    """Save credentials to ~/.trelent/agents/config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config = {"client_id": client_id, "client_secret": client_secret}
    if api_url:
        config["api_url"] = api_url

    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")
    CONFIG_FILE.chmod(0o600)


def check_credentials(client_id: str, client_secret: str, api_url: str | None = None) -> tuple[bool, str]:
    """Check if credentials are valid by making an authenticated API call.

    Returns (success, message) tuple.
    """
    url = api_url or DEFAULT_API_URL

    try:
        client = Client(
            api_url=url,
            client_id=client_id,
            client_secret=client_secret,
        )
        # Try listing runs - this requires auth and validates credentials
        client.runs.list()
        return True, f"Connected to {url}"
    except Exception as e:
        return False, str(e)


def get_client() -> Client:
    """Create an authenticated client from env vars or config file."""
    client_id = os.environ.get("TRELENT_CLIENT_ID")
    client_secret = os.environ.get("TRELENT_CLIENT_SECRET")
    api_url = os.environ.get("TRELENT_API_URL")

    if not client_id or not client_secret:
        config = load_config()
        client_id = client_id or config.get("client_id")
        client_secret = client_secret or config.get("client_secret")
        api_url = api_url or config.get("api_url")

    if not client_id or not client_secret:
        print("Error: Missing credentials.", file=sys.stderr)
        print("Run 'trelent auth' or set TRELENT_CLIENT_ID and TRELENT_CLIENT_SECRET.", file=sys.stderr)
        sys.exit(1)

    return Client(
        api_url=api_url or DEFAULT_API_URL,
        client_id=client_id,
        client_secret=client_secret,
    )
