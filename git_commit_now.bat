@echo off
cd /d d:\vscode\OnboardIQ
git --no-pager status
git --no-pager add scripts/ingest_data.py
git --no-pager add data/raw/customers.csv
git --no-pager add data/raw/transactions.json
git --no-pager add data/processed/customers_ingested.csv
git --no-pager add data/processed/transactions_ingested.csv
git --no-pager commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."
git --no-pager log -1
