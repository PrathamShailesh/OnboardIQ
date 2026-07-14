import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Simple check without capturing
print("Checking git state...")

# Status
print("\n=== Git Status ===")
subprocess.run(['git', 'status'], shell=False)

# Log
print("\n=== Git Log ===")
subprocess.run(['git', 'log', '--oneline', '-3'], shell=False)

# Branch
print("\n=== Current Branch ===")
subprocess.run(['git', 'branch', '--show-current'], shell=False)
