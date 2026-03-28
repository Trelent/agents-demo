# Trelent Agents Demo

A demo showing how to build, deploy, and run agents with Trelent.

## Sandboxes

| Sandbox | Tools | Use Case |
|---------|-------|----------|
| `translator` | `trans` CLI | Text translation |
| `data-handler` | `csvkit` | CSV processing & analysis |

## Prerequisites

- Docker installed and running
- Python 3.11+
- `trelent-agents` package installed (`uv sync` or `pip install trelent-agents`)

## 1. Build and Push Sandboxes

Build and push sandbox images to the Trelent registry:

```bash
# Translator sandbox
docker build -t agents.trelent.com/translator:latest translator-agent/
docker push agents.trelent.com/translator:latest

# Data handler sandbox
docker build -t agents.trelent.com/data-handler:latest data-handler/
docker push agents.trelent.com/data-handler:latest
```

## 2. Register the Agent

Register the sandbox and verify it's available:

```bash
# List available sandboxes
python src/register_agent.py

# Register the sandbox (first time only)
python src/register_agent.py --register
```

## 3. Create a Run

Create a simple translation run:

```bash
python src/create_run.py
```

This outputs a **Run ID** that you'll use in the next steps.

## 4. Track the Run

Poll the run until it completes:

```bash
python src/track_run.py <run_id>
```

The script polls every 2 seconds and prints the result when done.

## 5. Fork the Run

Fork an existing run with a new prompt:

```bash
python src/fork_run.py <run_id> "Translate to French instead"
python src/fork_run.py <run_id> "Summarize all translations"
```

Forking inherits the parent's sandbox and model.

## 6. Using Imports

Import local files for batch processing:

```bash
# Import ./input/ files and translate them
python src/create_run_with_import.py

# Same as above, but export results to S3
python src/create_run_with_export.py
```

Sample files in `input/`:
- `greeting.txt` - Welcome message
- `menu.txt` - Restaurant menu  
- `instructions.txt` - Assembly instructions
- `sales.csv` - Sales transactions
- `customers.csv` - Customer records
- `inventory.csv` - Inventory levels

Imported files are available at `/mnt/` inside the sandbox.

## Scripts Reference

| Script | Description |
|--------|-------------|
| `register_agent.py` | Register sandbox, list available sandboxes |
| `create_run.py` | Create a simple translation run |
| `create_run_with_import.py` | Create run with local file imports |
| `create_run_with_export.py` | Create run with imports + S3 export |
| `track_run.py` | Poll run status until completion |
| `fork_run.py` | Fork a run with a new prompt |

## Example Workflow

```bash
# 1. Push sandboxes
docker build -t agents.trelent.com/translator:latest translator-agent/
docker push agents.trelent.com/translator:latest

docker build -t agents.trelent.com/data-handler:latest data-handler/
docker push agents.trelent.com/data-handler:latest

# 2. Register
python src/register_agent.py --register

# 3. Create run with imports
python src/create_run_with_import.py
# Output: Run ID: run_abc123

# 4. Track it
python src/track_run.py run_abc123

# 5. Fork to another language
python src/fork_run.py run_abc123 "Translate to German"
# Output: Child Run ID: run_def456

# 6. Track the fork
python src/track_run.py run_def456
```
