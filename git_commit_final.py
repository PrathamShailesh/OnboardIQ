import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Simple git operations
commands = [
    ['git', 'status'],
    ['git', 'add', 'data/raw/customers.csv'],
    ['git', 'add', 'data/raw/transactions.json'],
    ['git', 'add', 'data/processed/customers_ingested.csv'],
    ['git', 'add', 'data/processed/transactions_ingested.csv'],
    ['git', 'commit', '-m', 'feat: implement multi-format data ingestion'],
    ['git', 'log', '-1']
]

for cmd in commands:
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT: {result.stdout}")
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    print()
