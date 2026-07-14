import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Try to run git status directly
print("Attempting git status...")
try:
    result = subprocess.run(['git', 'status'], check=True, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
except Exception as e:
    print("Error:", e)

# Try with shell=True
print("\nAttempting git status with shell=True...")
try:
    result = subprocess.run('git status', shell=True, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
except Exception as e:
    print("Error:", e)
