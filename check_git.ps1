cd d:\vscode\OnboardIQ
Write-Host "Git Status:"
git status
Write-Host "`nGit Add:"
git add scripts/ingest_data.py data/raw/ data/processed/
Write-Host "`nGit Commit:"
git commit -m "feat: implement multi-format data ingestion

Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files."
Write-Host "`nDone."
