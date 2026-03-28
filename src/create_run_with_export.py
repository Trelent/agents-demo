#!/usr/bin/env python3
"""Create a run with imports and S3 export for persisting results."""
from trelent_agents import Client, LocalImporter, S3Exporter

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
        exports=[
            S3Exporter(),
        ],
    )

    print(f"Run ID: {run.id}")
    print(f"Status: {run.status}")
    print("\nFiles imported from ./input/ -> /mnt/")
    print("Results will export to S3 when complete")

if __name__ == "__main__":
    main()
