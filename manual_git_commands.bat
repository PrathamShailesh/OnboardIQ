@echo off
cd /d d:\vscode\OnboardIQ
git add data/raw/customers.csv
git add data/raw/transactions.json  
git add data/processed/customers_ingested.csv
git add data/processed/transactions_ingested.csv
git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."
git log -1
