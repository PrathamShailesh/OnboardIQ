@echo off
cd /d d:\vscode\OnboardIQ
git add scripts/ingest_data.py
git add data/raw/customers.csv
git add data/raw/transactions.json
git add data/processed/customers_ingested.csv
git add data/processed/transactions_ingested.csv
