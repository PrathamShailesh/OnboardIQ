@echo off
cd /d d:\vscode\OnboardIQ
call git status
call git add scripts/ingest_data.py
call git add data/raw/customers.csv
call git add data/raw/transactions.json
call git add data/processed/customers_ingested.csv
call git add data/processed/transactions_ingested.csv
call git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."
