import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Get git log
result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
print("Git Log:")
print(result.stdout)
print("STDERR:")
print(result.stderr)

# Get current branch
result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
print("\nCurrent Branch:")
print(result.stdout)
print("STDERR:")
print(result.stderr)

# Get last commit hash
result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
print("\nLast Commit Hash:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
