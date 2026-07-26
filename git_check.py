import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Check if .git exists
print("Checking for .git directory...")
if os.path.exists('.git'):
    print(".git directory exists")
else:
    print(".git directory does NOT exist")

# Try to run git status with full output
print("\nAttempting git status with full path...")
try:
    result = subprocess.run(
        [r'C:\Program Files\Git\bin\git.exe', 'status'],
        capture_output=True,
        text=True,
        check=False,
        cwd=r'd:\vscode\OnboardIQ'
    )
    print(f"Return code: {result.returncode}")
    print(f"STDOUT length: {len(result.stdout)}")
    print(f"STDERR length: {len(result.stderr)}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
except Exception as e:
    print(f"Exception: {e}")

# Try without capture
print("\nAttempting git status without capture...")
try:
    result = subprocess.run(
        [r'C:\Program Files\Git\bin\git.exe', 'status'],
        check=False,
        cwd=r'd:\vscode\OnboardIQ'
    )
    print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"Exception: {e}")
