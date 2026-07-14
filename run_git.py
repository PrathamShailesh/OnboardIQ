import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

print("=== Git Status ===")
result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

print("\n=== Git Add ===")
result = subprocess.run(['git', 'add', 'scripts/ingest_data.py', 'data/raw/', 'data/processed/'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

print("\n=== Git Commit ===")
commit_msg = """feat: implement multi-format data ingestion

Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files."""
result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

print("\n=== Done ===")
