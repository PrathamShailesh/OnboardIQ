import os

os.chdir(r'd:\vscode\OnboardIQ')

print("Checking repository status:")
print(f".git exists: {os.path.exists('.git')}")
print(f".git is directory: {os.path.isdir('.git')}")

if os.path.exists('.git'):
    print("\n.git directory contents:")
    try:
        for item in os.listdir('.git'):
            print(f"  {item}")
    except Exception as e:
        print(f"  Error: {e}")

print(f"\nCurrent directory: {os.getcwd()}")
print(f"scripts/ingest_data.py exists: {os.path.exists('scripts/ingest_data.py')}")
print(f"data/raw/customers.csv exists: {os.path.exists('data/raw/customers.csv')}")
