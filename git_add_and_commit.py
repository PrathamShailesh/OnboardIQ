import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Add files
print("Adding files...")
subprocess.run(['git', 'add', 'data/raw/customers.csv'], check=False)
subprocess.run(['git', 'add', 'data/raw/transactions.json'], check=False)
subprocess.run(['git', 'add', 'data/processed/customers_ingested.csv'], check=False)
subprocess.run(['git', 'add', 'data/processed/transactions_ingested.csv'], check=False)

# Commit
print("Committing...")
subprocess.run(['git', 'commit', '-m', 'feat: implement multi-format data ingestion'], check=False)

# Check log
print("Checking log...")
subprocess.run(['git', 'log', '-1'], check=False)

print("Done")
