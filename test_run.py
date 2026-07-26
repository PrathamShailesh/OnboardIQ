import sys
sys.path.insert(0, 'd:\\vscode\\OnboardIQ')

# Import and run the ingestion script
import scripts.ingest_data as ingest_data

if __name__ == "__main__":
    # Call the main execution
    exec(open('scripts/ingest_data.py').read())
