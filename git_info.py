import subprocess
import os

os.chdir(r'd:\vscode\OnboardIQ')

# Try to get git info without capturing
print("Getting git info...")

# Use Popen to get output in real-time
process = subprocess.Popen(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate()
print("STDOUT:", stdout)
print("STDERR:", stderr)

# Get branch
process = subprocess.Popen(['git', 'branch', '--show-current'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate()
print("Branch:", stdout)
print("STDERR:", stderr)

# Get log
process = subprocess.Popen(['git', 'log', '--oneline', '-3'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = process.communicate()
print("Log:", stdout)
print("STDERR:", stderr)
