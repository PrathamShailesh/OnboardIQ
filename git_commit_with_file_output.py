import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Open a file to write all output
with open('git_commit_output.log', 'w') as log:
    def run_and_log(cmd):
        log.write(f"\n{'='*60}\n")
        log.write(f"Running: {cmd}\n")
        log.write(f"{'='*60}\n")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        log.write(f"Return code: {result.returncode}\n")
        if result.stdout:
            log.write(f"STDOUT:\n{result.stdout}\n")
        if result.stderr:
            log.write(f"STDERR:\n{result.stderr}\n")
        return result

    # Check status
    run_and_log('git status')

    # Add files individually
    run_and_log('git add data/raw/customers.csv')
    run_and_log('git add data/raw/transactions.json')
    run_and_log('git add data/processed/customers_ingested.csv')
    run_and_log('git add data/processed/transactions_ingested.csv')

    # Commit
    run_and_log('git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."')

    # Check log
    run_and_log('git log -1')

    log.write("\n=== Done ===\n")

print("Git operations completed. Check git_commit_output.log")
