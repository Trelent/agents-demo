#!/usr/bin/env python3
"""Create a new translation run and print the run ID."""
from trelent_agents import Client

SANDBOX_NAME = "translator:latest"

def main():
    client = Client()
    
    run = client.runs.create(
        sandbox=SANDBOX_NAME,
        model="claude-sonnet-4-5",
        prompt="""
Read /skills/translator.md to learn what tools you have.
Translate "The weather is nice today." to Spanish.
""",
    )
    
    print(f"Run ID: {run.id}")
    print(f"Status: {run.status}")

if __name__ == "__main__":
    main()
