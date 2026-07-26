import os
import sys

# Ensure we're in the right directory
os.chdir(r'd:\vscode\OnboardIQ')
print(f"Current directory: {os.getcwd()}")

# Create directories
os.makedirs('data/processed', exist_ok=True)
print("Created data/processed directory")

# Import and execute the ingestion script
exec(open('scripts/ingest_data.py').read())
