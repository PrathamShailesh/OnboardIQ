import os

os.chdir(r'd:\vscode\OnboardIQ')

# Check if files exist
files_to_check = [
    'scripts/ingest_data.py',
    'data/raw/customers.csv',
    'data/raw/transactions.json',
    'data/processed/customers_ingested.csv',
    'data/processed/transactions_ingested.csv'
]

print("Checking file existence:")
for f in files_to_check:
    exists = os.path.exists(f)
    print(f"  {f}: {'EXISTS' if exists else 'MISSING'}")

# Check .git directory
print(f"\n.git exists: {os.path.exists('.git')}")
