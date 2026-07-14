$ErrorActionPreference = "Continue"
cd d:\vscode\OnboardIQ

"=== Git Status ===" | Out-File -FilePath git_output.txt
git status | Out-File -FilePath git_output.txt -Append

"`n=== Git Add ===" | Out-File -FilePath git_output.txt -Append
git add scripts/ingest_data.py data/raw/ data/processed/ | Out-File -FilePath git_output.txt -Append

"`n=== Git Commit ===" | Out-File -FilePath git_output.txt -Append
git commit -m "feat: implement multi-format data ingestion

Loads CSV with explicit delimiter/encoding parameters.
Loads JSON with nested structure flattening.
Documents all ingestion with shape, dtypes, and sample rows.
Handles encoding fallback for non-standard files." | Out-File -FilePath git_output.txt -Append

"`n=== Done ===" | Out-File -FilePath git_output.txt -Append
Get-Content git_output.txt
