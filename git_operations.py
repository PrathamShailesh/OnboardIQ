import subprocess
import os
import sys

os.chdir(r'd:\vscode\OnboardIQ')

# Open a log file
with open('git_operations_log.txt', 'w') as log:
    def run_git_command(args):
        log.write(f"\n{'='*60}\n")
        log.write(f"Running: git {' '.join(args)}\n")
        log.write(f"{'='*60}\n")
        
        try:
            result = subprocess.run(
                ['C:\\Program Files\\Git\\bin\\git.exe'] + args,
                capture_output=True,
                text=True,
                check=False
            )
            log.write(f"Return code: {result.returncode}\n")
            if result.stdout:
                log.write(f"STDOUT:\n{result.stdout}\n")
            if result.stderr:
                log.write(f"STDERR:\n{result.stderr}\n")
            return result
        except Exception as e:
            log.write(f"Exception: {e}\n")
            return None

    # Check git status
    run_git_command(['status'])

    # Add files
    run_git_command(['add', 'scripts/ingest_data.py'])
    run_git_command(['add', 'data/raw/customers.csv'])
    run_git_command(['add', 'data/raw/transactions.json'])
    run_git_command(['add', 'data/processed/customers_ingested.csv'])
    run_git_command(['add', 'data/processed/transactions_ingested.csv'])

    # Commit
    commit_msg = """feat: implement multi-format data ingestion

Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files."""
    
    # Use -m for each line
    run_git_command(['commit', '-m', 'feat: implement multi-format data ingestion'])
    run_git_command(['commit', '-m', 'Loads CSV with explicit delimiter/encoding parameters.'])
    run_git_command(['commit', '-m', 'Loads JSON with nested structure flattening.'])
    run_git_command(['commit', '-m', 'Documents all ingestion with shape, dtypes, and sample rows.'])
    run_git_command(['commit', '-m', 'Handles encoding fallback for non-standard files.'])

    log.write("\n=== Operations Complete ===\n")

print("Git operations completed. Check git_operations_log.txt for details.")
