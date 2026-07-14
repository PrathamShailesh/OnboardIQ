@echo off
cd /d d:\vscode\OnboardIQ
git status
git add scripts/ingest_data.py data/raw/customers.csv data/raw/transactions.json data/processed/customers_ingested.csv data/processed/transactions_ingested.csv
git commit -m "feat: implement multi-format data ingestion
Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files."
