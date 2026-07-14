import subprocess
import os
import sys

os.chdir(r'd:\vscode\OnboardIQ')

# Try to add files using different methods
print("Method 1: subprocess with full path")
try:
    result = subprocess.run(
        [r'C:\Program Files\Git\bin\git.exe', 'add', 'scripts/ingest_data.py'],
        capture_output=False,
        text=True
    )
    print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"Error: {e}")

print("\nMethod 2: os.system")
os.system(r'C:\Program Files\Git\bin\git.exe add scripts/ingest_data.py')

print("\nMethod 3: subprocess with shell=True")
try:
    result = subprocess.run(
        'git add scripts/ingest_data.py',
        shell=True,
        capture_output=False
    )
    print(f"Return code: {result.returncode}")
except Exception as e:
    print(f"Error: {e}")
