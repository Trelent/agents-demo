#!/usr/bin/env python3
"""Fork an existing run with a new prompt."""
import sys
from trelent_agents import Client, LocalImporter

def main():
    if len(sys.argv) < 3:
        print("Usage: python fork_run.py <parent_run_id> <prompt>")
        print('Example: python fork_run.py run_abc123 "Translate to French instead"')
        sys.exit(1)

    parent_run_id = sys.argv[1]
    prompt = sys.argv[2]

    client = Client()
    parent_run = client.runs.get(parent_run_id)

    child_run = parent_run.fork(
        prompt=prompt,
        imports=[
            LocalImporter(path="./input"),
        ],
    )

    print(f"Parent Run ID: {parent_run_id}")
    print(f"Child Run ID: {child_run.id}")
    print(f"Status: {child_run.status}")
    print(f"\nPrompt: {prompt}")

if __name__ == "__main__":
    main()
