"""
Multi-Format Data Ingestion Script

This module provides functions for ingesting CSV and JSON data files
with support for encoding fallback, nested JSON flattening, and detailed
ingestion documentation.
"""

import pandas as pd
import os


def ingest_csv(filepath, delimiter=',', encoding='utf-8', dtype_dict=None):
    """
    Load a CSV file with explicit parameters.
    
    Args:
        filepath (str): Path to the CSV file
        delimiter (str): Delimiter character (default: ',')
        encoding (str): File encoding (default: 'utf-8')
        dtype_dict (dict, optional): Dictionary mapping column names to data types
    
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame
    
    Raises:
        FileNotFoundError: If the file does not exist
        UnicodeDecodeError: If the file cannot be decoded with the specified encoding
    """
    try:
        # Load CSV with explicit parameters
        df = pd.read_csv(
            filepath,
            delimiter=delimiter,
            encoding=encoding,
            dtype=dtype_dict
        )
        
        # Print ingestion summary
        print(f"\n{'='*60}")
        print(f"CSV Ingestion Report")
        print(f"{'='*60}")
        print(f"File: {os.path.basename(filepath)}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Column names: {list(df.columns)}")
        print(f"{'='*60}\n")
        
        return df
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except UnicodeDecodeError:
        raise UnicodeDecodeError(
            encoding,
            b'',
            0,
            1,
            f"Unable to decode file {filepath} with encoding '{encoding}'"
        )


def ingest_json(filepath, is_nested=False):
    """
    Load a JSON file with optional nested structure flattening.
    
    Args:
        filepath (str): Path to the JSON file
        is_nested (bool): Whether to flatten nested JSON structures (default: False)
    
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame
    """
    # Load JSON using pandas
    df = pd.read_json(filepath)
    
    # Flatten nested JSON if required
    if is_nested:
        df = pd.json_normalize(df.to_dict(orient='records'))
        flattened = True
    else:
        flattened = False
    
    # Print ingestion summary
    print(f"\n{'='*60}")
    print(f"JSON Ingestion Report")
    print(f"{'='*60}")
    print(f"File loaded: {os.path.basename(filepath)}")
    print(f"Shape: {df.shape}")
    print(f"Nested JSON flattened: {flattened}")
    print(f"{'='*60}\n")
    
    return df


def ingest_csv_with_fallback(filepath):
    """
    Attempt to load a CSV file with multiple encoding and delimiter combinations.
    
    Tries combinations of:
    - Encodings: utf-8, latin-1, iso-8859-1, cp1252
    - Delimiters: ',', ';', '\t'
    
    Stops immediately when a combination succeeds.
    
    Args:
        filepath (str): Path to the CSV file
    
    Returns:
        pd.DataFrame: Loaded data as a pandas DataFrame
    
    Raises:
        Exception: If all encoding/delimiter combinations fail
    """
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    delimiters = [',', ';', '\t']
    
    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
                print(f"Successfully loaded with encoding='{encoding}' and delimiter='{delimiter}'")
                return df
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    
    raise Exception(
        f"Unable to load dataset '{filepath}' with any combination of "
        f"encodings {encodings} and delimiters {delimiters}"
    )


def document_ingestion(df, source_file):
    """
    Display detailed documentation about the ingested dataset.
    
    Args:
        df (pd.DataFrame): The ingested DataFrame
        source_file (str): Path to the source file
    """
    print(f"\n{'='*60}")
    print(f"Ingestion Documentation")
    print(f"{'='*60}")
    print(f"Source file: {os.path.basename(source_file)}")
    print(f"Dataset shape: {df.shape}")
    print(f"\nColumn names:")
    for col in df.columns:
        print(f"  - {col}")
    print(f"\nData types:")
    print(df.dtypes)
    print(f"\nNull values:")
    print(df.isnull().sum())
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Ensure output directories exist
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Task 1: Load CSV
    print("\n" + "="*60)
    print("Loading CSV Data")
    print("="*60)
    customers_df = ingest_csv('data/raw/customers.csv')
    document_ingestion(customers_df, 'data/raw/customers.csv')
    
    # Task 2: Load JSON
    print("\n" + "="*60)
    print("Loading JSON Data")
    print("="*60)
    transactions_df = ingest_json('data/raw/transactions.json', is_nested=False)
    document_ingestion(transactions_df, 'data/raw/transactions.json')
    
    # Save processed outputs
    customers_df.to_csv('data/processed/customers_ingested.csv', index=False)
    transactions_df.to_csv('data/processed/transactions_ingested.csv', index=False)
    
    print("\n" + "="*60)
    print("SUCCESS: All datasets ingested successfully")
    print("="*60)
    print("Processed files saved:")
    print("  - data/processed/customers_ingested.csv")
    print("  - data/processed/transactions_ingested.csv")
    print("="*60 + "\n")
