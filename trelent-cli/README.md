# Trelent CLI

CLI for managing Trelent agent sandboxes and runs.

## Quickstart

```bash
# Install
cd trelent-cli
uv tool install .

# Authenticate
trelent auth add
# → prompts for client ID, secret, API URL, registry URL

# Build and push a sandbox
trelent sandboxes build ./agents/my-agent

# Create a run
trelent runs create -s my-agent:latest -p "Do the thing"

# Track it
trelent runs track --latest
```

## Installation

```bash
cd trelent-cli
uv tool install .
```

Or for development:

```bash
cd trelent-cli
uv sync
uv tool install . --force  # reinstall after changes
```

## Authentication

### Using profiles (recommended)

```bash
# Add a profile (interactive)
trelent auth add prod

# Add with flags (all options)
trelent auth add dev \
  --id YOUR_CLIENT_ID \
  --secret YOUR_SECRET \
  --api-url https://api.dev.trelent.com/agent \
  --registry-url registry.dev.trelent.com \
  --skip-verify  # optional: skip credential check

# List profiles
trelent auth list

# Switch profiles
trelent auth use prod

# Show current profile
trelent auth show

# Test credentials
trelent auth test

# Get a JWT token (for debugging)
trelent auth token
```

### Using environment variables

```bash
export TRELENT_CLIENT_ID="your-client-id"
export TRELENT_CLIENT_SECRET="your-client-secret"
export TRELENT_API_URL="https://api.dev.trelent.com/agent"  # optional
export TRELENT_PROFILE="prod"  # optional, use a specific profile
```

## Commands

### Sandboxes

Build and push Docker images to your registry:

```bash
# Build using folder name as image name (→ my-agent:latest)
trelent sandboxes build ./agents/my-agent

# Custom name:tag
trelent sandboxes build -t custom-name:v2 ./agents/my-agent

# List available sandboxes
trelent sandboxes list

# Get sandbox details
trelent sandboxes get my-agent:latest
```

### Runs

```bash
# List recent runs
trelent runs list
trelent runs list -n 20  # show 20 most recent

# Create a run
trelent runs create -s translator:latest -p "Translate hello to Spanish"
trelent runs create -s translator:latest -p "Translate files" -i ./input/  # with local files

# Track a run until completion
trelent runs track <run-id>
trelent runs track --latest
trelent runs track -l -p 5  # poll every 5 seconds

# Get run details
trelent runs get <run-id>
trelent runs get --latest

# Fork a run with a new prompt
trelent runs fork <run-id> -p "Now translate to German"
trelent runs fork --latest -p "Summarize the output"
```

### Command Aliases

For convenience:

| Full | Aliases |
|------|---------|
| `sandboxes` | `s`, `sbx`, `sandbox` |
| `runs` | `r`, `run` |

```bash
trelent s build ./agents/my-agent
trelent r list
```

### Per-command profile

Use `-p` to override the active profile for a single command:

```bash
trelent -p prod runs list
trelent -p dev sandboxes build ./agents/my-agent
```

## Example Workflow

```bash
# 1. Set up authentication
trelent auth add prod

# 2. Build and push your agent
trelent s build ./agents/translator-agent

# 3. Create a run with input files
trelent r create -s translator-agent:latest -p "Translate all files" -i ./input/

# 4. Track until complete
trelent r track --latest

# 5. Fork with a different prompt
trelent r fork --latest -p "Now translate to German"
```

## File Imports

When creating a run with `-i ./path/`, local files are uploaded and available at `/mnt/` inside the sandbox.

```bash
trelent runs create -s data-handler:latest -p "Analyze the CSV" -i ./data/
# Files in ./data/ are available at /mnt/ in the sandbox
```
