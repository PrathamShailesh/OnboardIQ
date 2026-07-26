@echo off
cd /d d:\vscode\OnboardIQ
git status > git_status.log 2>&1
git add scripts/ingest_data.py data/raw/customers.csv data/raw/transactions.json data/processed/customers_ingested.csv data/processed/transactions_ingested.csv >> git_status.log 2>&1
git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files." >> git_status.log 2>&1
git log -1 >> git_status.log 2>&1
