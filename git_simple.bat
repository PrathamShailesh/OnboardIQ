@echo off
cd /d d:\vscode\OnboardIQ
C:\Program Files\Git\bin\git.exe status
C:\Program Files\Git\bin\git.exe add scripts/ingest_data.py
C:\Program Files\Git\bin\git.exe add data/raw/customers.csv
C:\Program Files\Git\bin\git.exe add data/raw/transactions.json
C:\Program Files\Git\bin\git.exe add data/processed/customers_ingested.csv
C:\Program Files\Git\bin\git.exe add data/processed/transactions_ingested.csv
C:\Program Files\Git\bin\git.exe commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."
