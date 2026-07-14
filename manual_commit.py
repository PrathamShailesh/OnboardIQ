import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Simple direct execution
print("Running git status...")
os.system('git status')

print("\nAdding files...")
os.system('git add scripts/ingest_data.py')
os.system('git add data/raw/customers.csv')
os.system('git add data/raw/transactions.json')
os.system('git add data/processed/customers_ingested.csv')
os.system('git add data/processed/transactions_ingested.csv')

print("\nCommitting...")
os.system('git commit -m "feat: implement multi-format data ingestion"')

print("\nDone")
