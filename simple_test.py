import pandas as pd
import os

# Test pandas import
print("Testing pandas import...")
print(f"Pandas version: {pd.__version__}")

# Test CSV reading
print("\nReading CSV...")
df = pd.read_csv('data/raw/customers.csv')
print(f"CSV loaded successfully")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(df.head())

# Test JSON reading
print("\nReading JSON...")
df2 = pd.read_json('data/raw/transactions.json')
print(f"JSON loaded successfully")
print(f"Shape: {df2.shape}")
print(f"Columns: {list(df2.columns)}")
print(df2.head())

# Create processed directory
os.makedirs('data/processed', exist_ok=True)

# Save outputs
df.to_csv('data/processed/customers_ingested.csv', index=False)
df2.to_csv('data/processed/transactions_ingested.csv', index=False)

print("\nFiles saved successfully!")
print("SUCCESS")
