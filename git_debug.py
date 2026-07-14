import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

print("=== Git Debug ===")
print(f"Current directory: {os.getcwd()}")
print(f".git exists: {os.path.exists('.git')}")

# Try to get git config
print("\n=== Git Config ===")
result = subprocess.run(['git', 'config', '--list'], capture_output=True, text=True)
print(f"Return code: {result.returncode}")
print(f"STDOUT: {result.stdout[:500] if result.stdout else 'None'}")
print(f"STDERR: {result.stderr[:500] if result.stderr else 'None'}")

# Try git status
print("\n=== Git Status ===")
result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(f"Return code: {result.returncode}")
print(f"STDOUT: {result.stdout[:500] if result.stdout else 'None'}")
print(f"STDERR: {result.stderr[:500] if result.stderr else 'None'}")

# Try git log
print("\n=== Git Log ===")
result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
print(f"Return code: {result.returncode}")
print(f"STDOUT: {result.stdout[:500] if result.stdout else 'None'}")
print(f"STDERR: {result.stderr[:500] if result.stderr else 'None'}")
