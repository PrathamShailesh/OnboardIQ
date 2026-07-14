import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Check if files are staged
print("=== Checking git status ===")
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print(f"Short status: {result.stdout}")

# Check last commit
print("\n=== Checking last commit ===")
result = subprocess.run(['git', 'log', '-1', '--oneline'], capture_output=True, text=True)
print(f"Last commit: {result.stdout}")

# Check current branch
print("\n=== Checking current branch ===")
result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
print(f"Current branch: {result.stdout}")

# Check if files exist
print("\n=== Checking file existence ===")
files = [
    'scripts/ingest_data.py',
    'data/raw/customers.csv',
    'data/raw/transactions.json',
    'data/processed/customers_ingested.csv',
    'data/processed/transactions_ingested.csv'
]
for f in files:
    print(f"{f}: {'EXISTS' if os.path.exists(f) else 'MISSING'}")
