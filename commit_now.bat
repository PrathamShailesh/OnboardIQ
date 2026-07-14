@echo off
cd /d d:\vscode\OnboardIQ
git status > status.txt 2>&1
type status.txt
git add scripts/ingest_data.py data/raw/customers.csv data/raw/transactions.json data/processed/customers_ingested.csv data/processed/transactions_ingested.csv
git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."
git log -1 > log.txt 2>&1
type log.txt
