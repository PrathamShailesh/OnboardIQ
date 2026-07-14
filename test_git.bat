@echo off
cd /d d:\vscode\OnboardIQ
echo Testing git... > test_git_output.txt
C:\Program Files\Git\bin\git.exe --version >> test_git_output.txt 2>&1
C:\Program Files\Git\bin\git.exe status >> test_git_output.txt 2>&1
C:\Program Files\Git\bin\git.exe add scripts/ingest_data.py >> test_git_output.txt 2>&1
C:\Program Files\Git\bin\git.exe add data/raw/customers.csv >> test_git_output.txt 2>&1
C:\Program Files\Git\bin\git.exe add data/raw/transactions.json >> test_git_output.txt 2>&1
C:\Program Files\Git\bin\git.exe add data/processed/customers_ingested.csv >> test_git_output.txt 2>&1
C:\Program Files\Git\bin\git.exe add data/processed/transactions_ingested.csv >> test_git_output.txt 2>&1
C:\Program Files\Git\bin\git.exe commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files." >> test_git_output.txt 2>&1
echo Done >> test_git_output.txt 2>&1
type test_git_output.txt
