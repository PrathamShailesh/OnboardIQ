import subprocess
import os
import sys

os.chdir(r'd:\vscode\OnboardIQ')

def run_command(cmd):
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    return result

# Check git status
run_command(['git', 'status'])

# Add files
run_command(['git', 'add', 'scripts/ingest_data.py', 'data/raw/', 'data/processed/'])

# Commit
commit_msg = """feat: implement multi-format data ingestion

Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files."""
run_command(['git', 'commit', '-m', commit_msg])

print("\n=== Done ===")
