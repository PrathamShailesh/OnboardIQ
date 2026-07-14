import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Run git commands and save output to file
with open('commit_results.txt', 'w') as f:
    f.write("=== Git Status ===\n")
    result = subprocess.run(['git', 'status'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    f.write("\n=== Git Add ===\n")
    result = subprocess.run(['git', 'add', 'scripts/ingest_data.py'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    result = subprocess.run(['git', 'add', 'data/raw/customers.csv'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    result = subprocess.run(['git', 'add', 'data/raw/transactions.json'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    result = subprocess.run(['git', 'add', 'data/processed/customers_ingested.csv'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    result = subprocess.run(['git', 'add', 'data/processed/transactions_ingested.csv'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    f.write("\n=== Git Commit ===\n")
    result = subprocess.run(['git', 'commit', '-m', 'feat: implement multi-format data ingestion'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)
    
    f.write("\n=== Git Log ===\n")
    result = subprocess.run(['git', 'log', '-1'], capture_output=True, text=True)
    f.write(result.stdout)
    f.write(result.stderr)

print("Done. Check commit_results.txt")
