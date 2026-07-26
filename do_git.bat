@echo off
cd /d d:\vscode\OnboardIQ
echo Running git status...
git status
echo.
echo Running git add...
git add scripts/ingest_data.py data/raw/ data/processed/
echo.
echo Running git commit...
git commit -m "feat: implement multi-format data ingestion" -m "Loads CSV with explicit delimiter/encoding parameters." -m "Loads JSON with nested structure flattening." -m "Documents all ingestion with shape, dtypes, and sample rows." -m "Handles encoding fallback for non-standard files."
echo.
echo Done.
