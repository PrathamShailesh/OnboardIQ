@echo off
cd /d d:\vscode\OnboardIQ
git --version > version.txt 2>&1
git status > status.txt 2>&1
git log --oneline -5 > log.txt 2>&1
echo Files created
type version.txt
type status.txt
type log.txt
