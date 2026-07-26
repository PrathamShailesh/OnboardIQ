@echo off
cd /d d:\vscode\OnboardIQ
git log --oneline -1 > commit_hash.txt 2>&1
git branch --show-current > branch_name.txt 2>&1
type commit_hash.txt
type branch_name.txt
