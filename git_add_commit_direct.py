import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Run git add without capturing output
print("Adding files...")
subprocess.run(['git', 'add', 'scripts/ingest_data.py'])
subprocess.run(['git', 'add', 'data/raw/customers.csv'])
subprocess.run(['git', 'add', 'data/raw/transactions.json'])
subprocess.run(['git', 'add', 'data/processed/customers_ingested.csv'])
subprocess.run(['git', 'add', 'data/processed/transactions_ingested.csv'])

print("Committing...")
subprocess.run(['git', 'commit', '-m', 'feat: implement multi-format data ingestion', 
                '-m', 'Loads CSV with explicit delimiter/encoding parameters.',
                '-m', 'Loads JSON with nested structure flattening.',
                '-m', 'Documents all ingestion with shape, dtypes, and sample rows.',
                '-m', 'Handles encoding fallback for non-standard files.'])

print("Done")
