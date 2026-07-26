@echo off
cd /d d:\vscode\OnboardIQ
echo Starting git operations... > commit_output.log
echo. >> commit_output.log
echo Git Status: >> commit_output.log
git status >> commit_output.log 2>&1
echo. >> commit_output.log
echo Adding files... >> commit_output.log
git add scripts/ingest_data.py >> commit_output.log 2>&1
git add data/raw/customers.csv >> commit_output.log 2>&1
git add data/raw/transactions.json >> commit_output.log 2>&1
git add data/processed/customers_ingested.csv >> commit_output.log 2>&1
git add data/processed/transactions_ingested.csv >> commit_output.log 2>&1
echo. >> commit_output.log
echo Committing... >> commit_output.log
git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files." >> commit_output.log 2>&1
echo. >> commit_output.log
echo Git Log: >> commit_output.log
git log -1 >> commit_output.log 2>&1
echo. >> commit_output.log
echo Done. >> commit_output.log
type commit_output.log
