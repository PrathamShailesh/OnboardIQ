@echo off
cd /d d:\vscode\OnboardIQ
git add scripts/ingest_data.py data/raw/ data/processed/
git commit -m "feat: implement multi-format data ingestion

Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files."
git status
