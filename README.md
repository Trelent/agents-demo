# Trelent Agents Demo

Quickstart for building and running agent sandboxes on the Trelent platform.

## Prerequisites

- Docker
- Python 3.11+ with [uv](https://docs.astral.sh/uv/)
- Trelent credentials (client ID + secret)

## 1. Install the CLI

```bash
uv sync
```

```bash
uv tool install ./trelent-cli
```

This installs `trelent` globally. To update after changes:

```bash
uv tool install ./trelent-cli --reinstall
```

## 2. Authenticate

Add a profile with your credentials:

```bash
trelent auth add dev --skip-verify
# Prompts for: Client ID, Client secret, API URL
```

Use `--skip-verify` if credential verification fails (e.g., network issues). Then test separately:

```bash
trelent auth test
```

Switch between profiles:

```bash
trelent auth list          # See all profiles
trelent auth use dev       # Set default
trelent -p prod <command>  # Use specific profile for one command
```

## 3. Build & Push a Sandbox Image

Create your agent as a folder under `agents/` with a `Dockerfile`:

```
agents/
├── build_and_push.sh
├── data-handler/
│   ├── Dockerfile
│   └── skills/
├── translator-agent/
│   └── ...
└── my-custom-agent/      # ← Your new agent
    ├── Dockerfile
    └── skills/
```

Then build and push using the folder name:

```bash
cd agents
./build_and_push.sh my-custom-agent        # Pushes as :latest
./build_and_push.sh my-custom-agent:v2     # Custom tag
```

The script handles Docker login, build, and push to `registry.dev.trelent.com/<client_id>/<agent>:<tag>`.

The image is automatically registered as a sandbox once pushed.

## 4. List Sandboxes

```bash
trelent sandboxes list
```

Output:

```
Available sandboxes:
  - data-handler:latest
  - translator-agent:latest
```

## 5. Create a Run

Basic run:

```bash
trelent runs create \
  -s data-handler:latest \
  -p "Analyze the CSV and show me the top 5 rows by revenue"
```

With local file import (mounted at `/mnt/`):

```bash
trelent runs create \
  -s data-handler:latest \
  -p "Parse /mnt/sales.csv and summarize the data" \
  -i ~/data/sales.csv
```

Track until completion with `-t`:

```bash
trelent runs create \
  -s translator-agent:latest \
  -p "Translate 'Hello world' to Japanese" \
  -t
```

## 6. Track & Manage Runs

```bash
trelent runs list              # Recent runs
trelent runs list -s data-handler:latest  # Filter by sandbox

trelent runs get <run-id>      # Get run details
trelent runs get --latest      # Most recent run

trelent runs track <run-id>    # Poll until complete
trelent runs track --latest    # Track most recent
```

## 7. Fork a Run

Continue from a previous run's state:

```bash
trelent runs fork <run-id> -p "Now group by region instead"
trelent runs fork --latest -p "Add a chart"
```

---

## Demo Agents

| Agent | Description | Example Prompt |
|-------|-------------|----------------|
| `data-handler` | CSV analysis with csvkit | `"Show stats for /mnt/data.csv"` |
| `translator-agent` | Text translation | `"Translate 'Good morning' to French"` |

## Sandbox Requirements

Custom sandbox images must:

- Use Alpine base (e.g., `python:3.12-alpine`)
- Install bash: `apk add --no-cache bash`
- Include keep-alive CMD
- Place skill docs in `/skills/`

See `agents/data-handler/Dockerfile` for a working example.
