@echo off
cd /d d:\vscode\OnboardIQ
echo Starting git operations...
git status > git_output.txt 2>&1
type git_output.txt
echo.
echo Adding files...
git add scripts/ingest_data.py data/raw/customers.csv data/raw/transactions.json data/processed/customers_ingested.csv data/processed/transactions_ingested.csv >> git_output.txt 2>&1
echo.
echo Committing...
git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files." >> git_output.txt 2>&1
echo.
echo Final status:
git status >> git_output.txt 2>&1
type git_output.txt
echo.
echo Done.
