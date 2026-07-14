import os

os.chdir(r'd:\vscode\OnboardIQ')

print("=== Using os.system for git commands ===")

# Add files
print("Adding files...")
os.system('git add scripts/ingest_data.py')
os.system('git add data/raw/customers.csv')
os.system('git add data/raw/transactions.json')
os.system('git add data/processed/customers_ingested.csv')
os.system('git add data/processed/transactions_ingested.csv')

# Commit
print("Committing...")
os.system('git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."')

# Check log
print("Checking log...")
os.system('git log -1')

print("Done")
