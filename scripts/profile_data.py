"""
Data Profiling & Quality Assessment Script

This script provides utilities to profile datasets and assess data quality.
It analyzes nulls, duplicates, numerical and categorical column statistics,
identifies data quality issues based on predefined thresholds, and exports
a detailed quality report in JSON format.
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path


def profile_nulls_and_duplicates(df: pd.DataFrame) -> dict:
    """
    Calculate null counts, null percentages, exact duplicate count, and duplicate percentage.

    Args:
        df (pd.DataFrame): The DataFrame to profile.

    Returns:
        dict: A dictionary containing null and duplicate profiling results.
    """
    total_rows = len(df)
    
    # Calculate nulls per column
    null_counts = df.isnull().sum().to_dict()
    null_percentages = {}
    for col, count in null_counts.items():
        pct = (count / total_rows * 100) if total_rows > 0 else 0.0
        null_percentages[col] = round(float(pct), 2)
        
    # Calculate duplicates
    duplicate_count = int(df.duplicated().sum())
    duplicate_pct = (duplicate_count / total_rows * 100) if total_rows > 0 else 0.0
    duplicate_percentage = round(float(duplicate_pct), 2)
    
    return {
        "null_counts": {k: int(v) for k, v in null_counts.items()},
        "null_percentages": null_percentages,
        "duplicate_count": duplicate_count,
        "duplicate_percentage": duplicate_percentage
    }


def profile_numerical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Automatically detect numerical columns and calculate summary statistics.

    For every numerical column, calculates: min, max, mean, median, std dev, and null count.
    All numerical values are rounded to two decimal places.

    Args:
        df (pd.DataFrame): The DataFrame to profile.

    Returns:
        pd.DataFrame: A summary DataFrame with stats as index and numerical columns as columns.
    """
    # Detect numerical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    stats = {}
    for col in numeric_cols:
        col_data = df[col]
        # Calculate stats safely (returning NaN if there are no values)
        has_data = col_data.notna().any()
        
        stats[col] = {
            "min": float(col_data.min()) if has_data else np.nan,
            "max": float(col_data.max()) if has_data else np.nan,
            "mean": float(col_data.mean()) if has_data else np.nan,
            "median": float(col_data.median()) if has_data else np.nan,
            "std": float(col_data.std()) if col_data.notna().sum() > 1 else np.nan,
            "null_count": int(col_data.isnull().sum())
        }
        
    summary_df = pd.DataFrame(stats)
    return summary_df.round(2)


def profile_categorical_columns(df: pd.DataFrame, top_n: int = 5) -> dict:
    """
    Profile categorical columns in the DataFrame.

    Reports number of unique values, top N most frequent values, and null count.

    Args:
        df (pd.DataFrame): The DataFrame to profile.
        top_n (int): Number of top frequent values to return.

    Returns:
        dict: A dictionary containing profiling details for categorical columns.
    """
    # Detect categorical columns (non-numeric)
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    
    result = {}
    for col in categorical_cols:
        val_counts = df[col].value_counts()
        top_vals = {str(k): int(v) for k, v in val_counts.head(top_n).items()}
        
        result[col] = {
            "unique_values": int(df[col].nunique()),
            "top_values": top_vals,
            "null_count": int(df[col].isnull().sum())
        }
    return result


def identify_quality_issues(
    df: pd.DataFrame,
    null_threshold: float = 30.0,
    duplicate_threshold: float = 5.0
) -> list:
    """
    Identify and flag data quality issues such as high nulls, duplicates, or invalid transaction values.

    Args:
        df (pd.DataFrame): The DataFrame to analyze.
        null_threshold (float): Percentage threshold above which nulls are considered high.
        duplicate_threshold (float): Percentage threshold above which duplicates are considered high.

    Returns:
        list: A list of dictionaries representing quality issues found.
    """
    issues = []
    total_rows = len(df)
    if total_rows == 0:
        return issues
        
    # 1. High Null Percentage
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct = (null_count / total_rows * 100)
        if null_pct > null_threshold:
            issues.append({
                "issue_type": "high_null_percentage",
                "column": col,
                "value": round(float(null_pct), 2),
                "severity": "HIGH",
                "recommendation": "Consider imputation or removing the column."
            })
            
    # 2. Duplicate Records
    duplicate_count = df.duplicated().sum()
    duplicate_pct = (duplicate_count / total_rows * 100)
    if duplicate_pct > duplicate_threshold:
        issues.append({
            "issue_type": "duplicate_records",
            "value": round(float(duplicate_pct), 2),
            "severity": "HIGH",
            "recommendation": "Deduplicate before further analysis."
        })
        
    # 3. Invalid Numeric Values (for numeric columns containing "amount")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if "amount" in col.lower():
            # Check for negative values
            negative_count = int((df[col] < 0).sum())
            if negative_count > 0:
                issues.append({
                    "issue_type": "invalid_numeric_values",
                    "column": col,
                    "value": negative_count,
                    "severity": "MEDIUM",
                    "recommendation": "Investigate negative transaction values."
                })
                
    return issues


def clean_nans(obj):
    """
    Recursively clean dictionary/list objects to replace NaN/NaT values with None for JSON serialization.

    Args:
        obj: The object to clean.

    Returns:
        The cleaned object with NaNs replaced by None.
    """
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nans(v) for v in obj]
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif pd.isna(obj):
        return None
    return obj


def generate_profile_report(df: pd.DataFrame, filepath: str) -> dict:
    """
    Generate a complete profiling report, save it as a JSON file, and print a summary.

    Args:
        df (pd.DataFrame): The DataFrame to profile.
        filepath (str): The output file path to save the JSON report.

    Returns:
        dict: The complete report dictionary.
    """
    # Deduce dataset name from output filepath or generic name
    dataset_name = "quality_test"
    
    # Calculate sub-profiles
    null_and_dup = profile_nulls_and_duplicates(df)
    null_analysis = {
        "null_counts": null_and_dup["null_counts"],
        "null_percentages": null_and_dup["null_percentages"]
    }
    duplicate_analysis = {
        "duplicate_count": null_and_dup["duplicate_count"],
        "duplicate_percentage": null_and_dup["duplicate_percentage"]
    }
    
    numerical_stats = profile_numerical_columns(df)
    categorical_stats = profile_categorical_columns(df)
    quality_issues = identify_quality_issues(df)
    
    # Compile the final report dict
    report = {
        "dataset_name": dataset_name,
        "record_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "null_analysis": null_analysis,
        "duplicate_analysis": duplicate_analysis,
        "numerical_statistics": clean_nans(numerical_stats.to_dict()),
        "categorical_statistics": clean_nans(categorical_stats),
        "data_quality_issues": quality_issues
    }
    
    # Save the report as JSON
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
        
    # Print a readable summary showing: Dataset, Record count, Column count, Total issues found, Severity, Recommendations
    print("\n" + "=" * 50)
    print("DATA QUALITY PROFILE SUMMARY")
    print("=" * 50)
    print(f"Dataset:             {dataset_name}")
    print(f"Record count:        {report['record_count']}")
    print(f"Column count:        {report['column_count']}")
    print(f"Total issues found:  {len(quality_issues)}")
    print("-" * 50)
    
    if quality_issues:
        print("Issues Details:")
        for idx, issue in enumerate(quality_issues, 1):
            print(f"\n  Issue #{idx}: {issue['issue_type']}")
            if "column" in issue:
                print(f"    Column:         {issue['column']}")
            print(f"    Value:          {issue['value']}")
            print(f"    Severity:       {issue['severity']}")
            print(f"    Recommendation: {issue['recommendation']}")
    else:
        print("No quality issues identified.")
    print("=" * 50 + "\n")
    
    return report


if __name__ == "__main__":
    try:
        # Load sample dataset
        data_path = "data/raw/quality_test.csv"
        print(f"Loading dataset: {data_path}")
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Sample dataset not found at {data_path}")
            
        df_test = pd.read_csv(data_path)
        
        # Execute profiling and generate report
        report_path = "output/profile_report.json"
        generate_profile_report(df_test, report_path)
        
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
        exit(1)
