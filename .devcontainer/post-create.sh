#!/bin/bash
set -e

echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Adding uv to PATH..."
export PATH="$HOME/.local/bin:$PATH"

echo "Installing trelent CLI..."
cd /workspaces/agents-demo/trelent-cli
uv tool install .

echo "Done! Run 'trelent --help' to get started."
