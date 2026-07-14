@echo off
cd /d d:\vscode\OnboardIQ
git log --oneline -5 > git_log_output.txt 2>&1
type git_log_output.txt
