@echo off
cd /d d:\vscode\OnboardIQ
C:\Program Files\Git\bin\git.exe status > git_status_output.txt 2>&1
C:\Program Files\Git\bin\git.exe add scripts/ingest_data.py data/raw/customers.csv data/raw/transactions.json data/processed/customers_ingested.csv data/processed/transactions_ingested.csv >> git_status_output.txt 2>&1
C:\Program Files\Git\bin\git.exe commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files." >> git_status_output.txt 2>&1
type git_status_output.txt
