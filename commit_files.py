import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Use full path to git
git_path = r'C:\Program Files\Git\bin\git.exe'

print("=== Git Status ===")
result = subprocess.run([git_path, 'status'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n=== Adding Files ===")
result = subprocess.run([git_path, 'add', 'scripts/ingest_data.py'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

result = subprocess.run([git_path, 'add', 'data/raw/customers.csv'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

result = subprocess.run([git_path, 'add', 'data/raw/transactions.json'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

result = subprocess.run([git_path, 'add', 'data/processed/customers_ingested.csv'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

result = subprocess.run([git_path, 'add', 'data/processed/transactions_ingested.csv'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n=== Committing ===")
commit_msg = """feat: implement multi-format data ingestion

Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files."""
result = subprocess.run([git_path, 'commit', '-m', commit_msg], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n=== Done ===")
