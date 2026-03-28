#!/usr/bin/env python3
"""Poll a run's status until completion and print the result."""
import sys
import time
from trelent_agents import Client

POLL_INTERVAL = 2  # seconds

def main():
    if len(sys.argv) < 2:
        print("Usage: python track_run.py <run_id>")
        sys.exit(1)
    
    run_id = sys.argv[1]
    client = Client()
    
    print(f"Tracking run: {run_id}")
    
    while True:
        run = client.runs.get(run_id)
        print(f"Status: {run.status}")
        
        if run.status in ("completed", "failed", "cancelled"):
            break
        
        time.sleep(POLL_INTERVAL)
    
    print("\n--- Result ---")
    print(run.result.output)

if __name__ == "__main__":
    main()
