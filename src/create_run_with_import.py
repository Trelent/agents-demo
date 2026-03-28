#!/usr/bin/env python3
"""Create a run with local file imports for batch translation."""
from trelent_agents import Client, LocalImporter

SANDBOX_NAME = "translator:latest"

def main():
    client = Client()

    run = client.runs.create(
        sandbox=SANDBOX_NAME,
        model="claude-sonnet-4-5",
        prompt="""
Read /skills/translator.md to learn your tools.
Translate all files in /mnt/ to Spanish.
Save translations to /output/.
""",
        imports=[
            LocalImporter(path="./input"),
        ],
    )

    print(f"Run ID: {run.id}")
    print(f"Status: {run.status}")
    print("\nFiles imported from ./input/ will be available at /mnt/")

if __name__ == "__main__":
    main()
