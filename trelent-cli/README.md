# Trelent Agents CLI

A CLI wrapper for the trelent-agents SDK.

## Sandboxes

| Sandbox | Tools | Use Case |
|---------|-------|----------|
| `translator` | `trans` CLI | Text translation |
| `data-handler` | `csvkit` | CSV processing & analysis |

## Installation

```bash
cd script
uv sync  # or pip install -e .
```

## Authentication

Set your credentials via environment variables:

```bash
export TRELENT_CLIENT_ID="your-client-id"
export TRELENT_CLIENT_SECRET="your-client-secret"
```

Optionally override the API URL:

```bash
export TRELENT_API_URL="https://agents.trelent.com"
```

## Commands

### List runs

```bash
agents runs
agents runs -n 20  # show 20 most recent
```

### Track a run

```bash
agents track run-123abc
agents track --latest       # track the most recent run
agents track -l -p 5        # poll every 5 seconds
```

### Get run details

```bash
agents get run-123abc
agents get --latest
```

### Create a run

```bash
agents create -s translator:latest -p "Translate hello to Spanish"
agents create -s translator:latest -m gpt-4o -p "Translate to French" -t  # track immediately
agents create -s translator:latest -p "Translate files" -i ./input/      # import local files
```

### Fork a run

```bash
agents fork run-123abc -p "Now translate to German"
agents fork --latest -p "Summarize the translations"
agents fork -l -p "New prompt" -i ./more-files/
```

### Manage sandboxes

```bash
agents sandboxes list
agents sandboxes register translator:latest
```

## Example Workflow

```bash
# 1. Push sandboxes to registry
docker build -t agents.trelent.com/translator:latest translator-agent/
docker push agents.trelent.com/translator:latest

# 2. Register the sandbox
agents sandboxes register translator:latest

# 3. Create a run with imports
agents create -s translator:latest -p "Translate all files in /mnt/" -i ./input/

# 4. Track the latest run
agents track --latest

# 5. Fork to another language
agents fork --latest -p "Translate to German instead"

# 6. Track the fork
agents track --latest
```

## Sample Files

Place files in `input/` for import:
- `greeting.txt` - Welcome message
- `menu.txt` - Restaurant menu  
- `instructions.txt` - Assembly instructions
- `sales.csv` - Sales transactions
- `customers.csv` - Customer records
- `inventory.csv` - Inventory levels

Imported files are available at `/mnt/` inside the sandbox.
