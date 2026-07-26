import subprocess
import os
import sys

os.chdir(r'd:\vscode\OnboardIQ')

# Open a file to write output
with open('git_log.txt', 'w') as f:
    def run_and_log(cmd):
        f.write(f"\n{'='*60}\n")
        f.write(f"Running: {' '.join(cmd)}\n")
        f.write(f"{'='*60}\n")
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        f.write(f"Return code: {result.returncode}\n")
        if result.stdout:
            f.write(f"STDOUT:\n{result.stdout}\n")
        if result.stderr:
            f.write(f"STDERR:\n{result.stderr}\n")
        return result

    # Check git status
    run_and_log(['git', 'status'])

    # Add files
    run_and_log(['git', 'add', 'scripts/ingest_data.py', 'data/raw/', 'data/processed/'])

    # Commit
    commit_msg = """feat: implement multi-format data ingestion

Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files."""
    run_and_log(['git', 'commit', '-m', commit_msg])

    f.write("\n=== Done ===\n")

print("Git operations completed. Check git_log.txt for output.")
