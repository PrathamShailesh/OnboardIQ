cd d:\vscode\OnboardIQ
$ErrorActionPreference = "Continue"

# Redirect all output to a file
Start-Transcript -Path "git_commit_log.txt" -Force

Write-Host "=== Git Status ==="
git status

Write-Host "`n=== Adding Files ==="
git add scripts/ingest_data.py
git add data/raw/customers.csv
git add data/raw/transactions.json
git add data/processed/customers_ingested.csv
git add data/processed/transactions_ingested.csv

Write-Host "`n=== Committing ==="
git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."

Write-Host "`n=== Done ==="

Stop-Transcript
