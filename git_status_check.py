import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Try to get git status with different methods
print("Method 1: subprocess.run with capture_output")
result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(f"Return code: {result.returncode}")
print(f"STDOUT length: {len(result.stdout)}")
print(f"STDERR length: {len(result.stderr)}")
if result.stdout:
    print(f"STDOUT:\n{result.stdout}")
if result.stderr:
    print(f"STDERR:\n{result.stderr}")

print("\nMethod 2: subprocess.run without capture")
result = subprocess.run(['git', 'status'])
print(f"Return code: {result.returncode}")

print("\nMethod 3: os.system")
exit_code = os.system('git status')
print(f"Exit code: {exit_code}")
