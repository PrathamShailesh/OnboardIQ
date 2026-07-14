import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Direct git commands
print("=== Direct Git Commands ===")

# Add files
print("Adding files...")
subprocess.run(['git', 'add', 'scripts/ingest_data.py'], shell=True)
subprocess.run(['git', 'add', 'data/raw/customers.csv'], shell=True)
subprocess.run(['git', 'add', 'data/raw/transactions.json'], shell=True)
subprocess.run(['git', 'add', 'data/processed/customers_ingested.csv'], shell=True)
subprocess.run(['git', 'add', 'data/processed/transactions_ingested.csv'], shell=True)

# Commit
print("Committing...")
subprocess.run(['git', 'commit', '-m', 'feat: implement multi-format data ingestion'], shell=True)

# Check log
print("Checking log...")
subprocess.run(['git', 'log', '-1'], shell=True)

print("Done")
