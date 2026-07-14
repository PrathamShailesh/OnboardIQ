import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Run git commands without capturing output
print("Running git add...")
subprocess.run(['git', 'add', 'scripts/ingest_data.py'], check=False)
subprocess.run(['git', 'add', 'data/raw/customers.csv'], check=False)
subprocess.run(['git', 'add', 'data/raw/transactions.json'], check=False)
subprocess.run(['git', 'add', 'data/processed/customers_ingested.csv'], check=False)
subprocess.run(['git', 'add', 'data/processed/transactions_ingested.csv'], check=False)

print("Running git commit...")
subprocess.run(['git', 'commit', '-m', 'feat: implement multi-format data ingestion', 
                '-m', 'Loads CSV with explicit delimiter/encoding parameters.',
                '-m', 'Loads JSON with nested structure flattening.',
                '-m', 'Documents all ingestion with shape, dtypes, and sample rows.',
                '-m', 'Handles encoding fallback for non-standard files.'], check=False)

print("Done")
