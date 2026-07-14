@echo off
cd /d d:\vscode\OnboardIQ
git status > git_status_result.txt 2>&1
echo Done. Check git_status_result.txt
