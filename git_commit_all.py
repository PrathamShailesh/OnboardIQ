import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Write output to file
with open('git_commit_all_output.txt', 'w') as f:
    f.write("=== Git Status ===\n")
    result = subprocess.run(['git', 'status'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    f.write("\n=== Adding Files ===\n")
    files = [
        'data/raw/customers.csv',
        'data/raw/transactions.json',
        'data/processed/customers_ingested.csv',
        'data/processed/transactions_ingested.csv'
    ]
    
    for file in files:
        result = subprocess.run(['git', 'add', file], capture_output=True, text=True)
        f.write(f"Added {file}: {result.returncode}\n")
        if result.stderr:
            f.write(f"  Error: {result.stderr}\n")
    
    f.write("\n=== Committing ===\n")
    result = subprocess.run(['git', 'commit', '-m', 'feat: implement multi-format data ingestion'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    f.write("\n=== Git Log ===\n")
    result = subprocess.run(['git', 'log', '-1'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)

print("Done. Check git_commit_all_output.txt")
