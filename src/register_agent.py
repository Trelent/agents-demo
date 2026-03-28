#!/usr/bin/env python3
"""Register the translator agent and list available sandboxes."""
import sys
from trelent_agents import Client

SANDBOX_NAME = "translator:latest"

def main():
    client = Client()
    
    if "--register" in sys.argv:
        print(f"Registering sandbox: {SANDBOX_NAME}")
        client.sandboxes.register(SANDBOX_NAME)
        print("Registration complete.")
    
    print("\nAvailable sandboxes:")
    sandboxes = client.sandboxes.list()
    for sandbox in sandboxes:
        print(f"  - {sandbox}")

if __name__ == "__main__":
    main()
