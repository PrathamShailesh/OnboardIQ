"""
handle_missing.py

This script detects, analyzes, and imputes missing values in datasets.
It implements multiple imputation strategies (median/mean, mode, forward-fill,
and row dropping) and logs business decisions and validation metrics.
"""

import os
import json
import pandas as pd
import numpy as np


def analyze_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes missing values in a DataFrame and prints a summary.

    Parameters:
    df (pd.DataFrame): The input DataFrame to analyze.

    Returns:
    pd.DataFrame: A DataFrame containing the analysis of missing values.
    """
    total_rows = len(df)
    total_cells = df.size
    total_missing_cells = int(df.isnull().sum().sum())

    analysis_data = []
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_percentage = (null_count / total_rows * 100) if total_rows > 0 else 0.0
        data_type = str(df[col].dtype)
        
        # Populate null meanings where appropriate
        null_meaning = ""
        if col == "customer_id":
            null_meaning = "Missing unique customer identifier"
        elif col == "email":
            null_meaning = "Missing contact email address"
        elif col == "amount":
            null_meaning = "Missing transaction amount"
        elif col == "category":
            null_meaning = "Missing purchase category"
        elif col == "name":
            null_meaning = "Missing customer name"
            
        analysis_data.append({
            "column": col,
            "data_type": data_type,
            "null_count": null_count,
            "null_percentage": float(null_percentage),
            "null_meaning": null_meaning
        })

    analysis_df = pd.DataFrame(analysis_data)

    print("=" * 60)
    print("MISSING VALUE ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Rows:          {total_rows}")
    print(f"Total Cells:         {total_cells}")
    print(f"Total Missing Cells: {total_missing_cells}")
    print("-" * 60)
    print(analysis_df.to_string(index=False))
    print("=" * 60)

    return analysis_df


def impute_mean_median(df: pd.DataFrame, numerical_cols: list, strategy: str = 'median') -> pd.DataFrame:
    """
    Imputes missing values in numerical columns using mean or median.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    numerical_cols (list): List of columns to impute.
    strategy (str): Imputation strategy, either 'median' or 'mean'. Default is 'median'.

    Returns:
    pd.DataFrame: The DataFrame with imputed numerical values.
    """
    df_copy = df.copy()
    if strategy not in ['mean', 'median']:
        raise ValueError("Strategy must be 'mean' or 'median'")

    print(f"\n--- Numerical Imputation (Strategy: {strategy}) ---")
    for col in numerical_cols:
        if col not in df_copy.columns:
            print(f"Column '{col}' not found in DataFrame. Skipping.")
            continue

        null_count = int(df_copy[col].isnull().sum())
        if strategy == 'mean':
            fill_value = df_copy[col].mean()
        else:
            fill_value = df_copy[col].median()

        # Handle case where all values in the column are null
        if pd.isnull(fill_value):
            fill_value = 0.0
            
        df_copy[col] = df_copy[col].fillna(fill_value)
        print(f"Column: {col} | Nulls Filled: {null_count} | Fill Value Used: {fill_value}")

    return df_copy


def impute_mode(df: pd.DataFrame, categorical_cols: list) -> pd.DataFrame:
    """
    Imputes missing values in categorical columns using the mode.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    categorical_cols (list): List of columns to impute.

    Returns:
    pd.DataFrame: The DataFrame with imputed categorical values.
    """
    df_copy = df.copy()
    print("\n--- Categorical Imputation (Strategy: mode) ---")
    for col in categorical_cols:
        if col not in df_copy.columns:
            print(f"Column '{col}' not found in DataFrame. Skipping.")
            continue

        null_count = int(df_copy[col].isnull().sum())
        mode_series = df_copy[col].mode()
        
        if not mode_series.empty:
            mode_value = mode_series[0]
        else:
            mode_value = "Unknown"
            
        df_copy[col] = df_copy[col].fillna(mode_value)
        print(f"Column: {col} | Nulls Filled: {null_count} | Mode Value Used: {mode_value}")

    return df_copy


def impute_forward_fill(df: pd.DataFrame, time_series_cols: list) -> pd.DataFrame:
    """
    Imputes missing values in time-series columns using forward fill (ffill).

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    time_series_cols (list): List of columns to impute.

    Returns:
    pd.DataFrame: The DataFrame with imputed time-series values.
    """
    df_copy = df.copy()
    print("\n--- Time-Series Imputation (Strategy: forward fill) ---")
    for col in time_series_cols:
        if col not in df_copy.columns:
            print(f"Column '{col}' not found in DataFrame. Skipping.")
            continue

        null_before = int(df_copy[col].isnull().sum())
        df_copy[col] = df_copy[col].ffill()
        null_after = int(df_copy[col].isnull().sum())
        filled_count = null_before - null_after
        
        print(f"Column: {col} | Nulls Filled: {filled_count}")

    return df_copy


def drop_rows_with_nulls(df: pd.DataFrame, critical_cols: list) -> pd.DataFrame:
    """
    Removes rows where critical columns contain null values.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    critical_cols (list): List of columns to check for null values.

    Returns:
    pd.DataFrame: The cleaned DataFrame with rows removed.
    """
    df_copy = df.copy()
    print("\n--- Drop Critical Rows ---")
    
    cols_to_check = [col for col in critical_cols if col in df_copy.columns]
    missing_cols = [col for col in critical_cols if col not in df_copy.columns]

    if missing_cols:
        print(f"Critical columns not found in DataFrame: {missing_cols}")

    if not cols_to_check:
        print("No critical columns found in DataFrame to check. No rows removed.")
        return df_copy

    initial_rows = len(df_copy)
    df_copy = df_copy.dropna(subset=cols_to_check)
    final_rows = len(df_copy)
    rows_removed = initial_rows - final_rows

    print(f"Rows Removed: {rows_removed}")
    return df_copy


def document_imputation_decisions(df_original: pd.DataFrame, df_imputed: pd.DataFrame) -> dict:
    """
    Documents imputation decisions and saves them to output/imputation_decisions.json.

    Parameters:
    df_original (pd.DataFrame): The original DataFrame before imputation.
    df_imputed (pd.DataFrame): The imputed/cleaned DataFrame.

    Returns:
    dict: The dictionary containing the imputation decisions.
    """
    os.makedirs("output", exist_ok=True)

    # Dictionary containing reasoning and strategy metadata for columns
    column_metadata = {
        "customer_id": {
            "strategy": "Drop Rows",
            "business_reasoning": "Customer ID is the unique primary identifier. Rows with missing customer ID are orphaned and cannot be associated with any entity.",
            "risk_assessment": "Low. Essential for relational integrity and accurate analytics."
        },
        "email": {
            "strategy": "Drop Rows",
            "business_reasoning": "Email address is critical for communications and identity resolution. Operating on rows with missing email poses compliance and communication risks.",
            "risk_assessment": "Low. Dropping ensures high-quality communications, but slightly reduces dataset size."
        },
        "amount": {
            "strategy": "Median Imputation",
            "business_reasoning": "Using the median transaction amount maintains distribution consistency and minimizes skew from extreme transaction outliers.",
            "risk_assessment": "Low. Prevents skewing the financial mean, but might reduce overall variance."
        },
        "quantity": {
            "strategy": "Median Imputation",
            "business_reasoning": "Quantity must be a positive integer. Imputing with the median prevents fractional quantities and skewed counts.",
            "risk_assessment": "Low. Safe default for transactional statistics."
        },
        "category": {
            "strategy": "Mode Imputation",
            "business_reasoning": "Mode imputation fills missing categorizations with the most common category, preserving qualitative data distributions.",
            "risk_assessment": "Low. Safe assuming missingness is low, but can over-represent the modal category."
        },
        "region": {
            "strategy": "Mode Imputation",
            "business_reasoning": "Assigns the most common geographic region to balance territorial marketing segmentation.",
            "risk_assessment": "Low. May introduce minor localized bias if region distribution is highly uniform."
        },
        "status_date": {
            "strategy": "Forward Fill",
            "business_reasoning": "Time-based status updates assume a record retains its state until the next chronologically recorded change.",
            "risk_assessment": "Medium. Assumes no changes occurred between log times, which might introduce temporal staleness."
        },
        "last_updated": {
            "strategy": "Forward Fill",
            "business_reasoning": "Timestamps of last update in sequential logs are forward-filled under the assumption of state persistence.",
            "risk_assessment": "Medium. Might delay the true status transition time, but preserves correct sequence ordering."
        }
    }

    decisions = {}

    for col, meta in column_metadata.items():
        if col in df_original.columns:
            null_count_before = int(df_original[col].isnull().sum())
            col_type = str(df_original[col].dtype)

            # Determine the actual value used during imputation
            value_used = None
            if meta["strategy"] == "Median Imputation":
                value_used = float(df_original[col].median()) if not pd.isnull(df_original[col].median()) else 0.0
            elif meta["strategy"] == "Mode Imputation":
                mode_val = df_original[col].mode()
                value_used = str(mode_val[0]) if not mode_val.empty else "Unknown"
            elif meta["strategy"] == "Forward Fill":
                value_used = "N/A (Forward Filled)"
            elif meta["strategy"] == "Drop Rows":
                value_used = "N/A (Rows Dropped)"
        else:
            # Handle required examples that may not exist in the raw dataframe
            null_count_before = 0
            col_type = "datetime64[ns]" if "date" in col or "updated" in col else "object"
            value_used = "N/A (Column not present in current dataset)"

        decisions[col] = {
            "column_type": col_type,
            "missing_value_count_before": null_count_before,
            "imputation_strategy": meta["strategy"],
            "value_used": value_used,
            "business_reasoning": meta["business_reasoning"],
            "risk_assessment": meta["risk_assessment"]
        }

    json_path = os.path.join("output", "imputation_decisions.json")
    with open(json_path, "w") as f:
        json.dump(decisions, f, indent=4)

    print(f"\nImputation decisions written to {json_path}")
    return decisions


def validate_imputation(df_original: pd.DataFrame, df_imputed: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the imputation results by comparing the before and after states.

    Parameters:
    df_original (pd.DataFrame): The original raw DataFrame.
    df_imputed (pd.DataFrame): The post-treatment cleaned DataFrame.

    Returns:
    pd.DataFrame: A DataFrame with the null status summary of the cleaned columns.
    """
    total_rows_before = len(df_original)
    total_rows_after = len(df_imputed)
    rows_removed = total_rows_before - total_rows_after

    total_nulls_before = int(df_original.isnull().sum().sum())
    total_nulls_after = int(df_imputed.isnull().sum().sum())

    print("\n" + "=" * 60)
    print("BEFORE & AFTER METRICS VALIDATION REPORT")
    print("=" * 60)
    print(f"Total Rows Before:  {total_rows_before}")
    print(f"Total Rows After:   {total_rows_after}")
    print(f"Rows Removed:       {rows_removed}")
    print(f"Total Nulls Before: {total_nulls_before}")
    print(f"Total Nulls After:  {total_nulls_after}")
    print("-" * 60)

    validation_data = []
    for col in df_imputed.columns:
        null_count_after = int(df_imputed[col].isnull().sum())
        null_pct_after = (null_count_after / total_rows_after * 100) if total_rows_after > 0 else 0.0

        validation_data.append({
            "column": col,
            "null_count_after": null_count_after,
            "null_percentage_after": float(null_pct_after)
        })

    validation_df = pd.DataFrame(validation_data)
    print("Post-Treatment Column Summary:")
    print(validation_df.to_string(index=False))
    print("=" * 60)

    return validation_df


if __name__ == "__main__":
    # 1. Load dataset
    raw_data_path = "data/raw/missing_data.csv"
    try:
        df_raw = pd.read_csv(raw_data_path)
        print(f"Loaded raw dataset from {raw_data_path}")
    except Exception as e:
        print(f"Error loading {raw_data_path}: {e}")
        import sys
        sys.exit(1)

    # 2. Analyze missing values
    df_analysis = analyze_missing_values(df_raw)

    # 3. Drop rows with nulls in critical columns
    df_working = drop_rows_with_nulls(df_raw, ["customer_id", "email"])

    # 4. Apply median imputation for amount and quantity (handle quantity gracefully)
    df_working = impute_mean_median(df_working, ["amount", "quantity"], strategy='median')

    # 5. Apply mode imputation for category and region (skip missing columns without failing)
    df_working = impute_mode(df_working, ["category", "region"])

    # 6. Apply forward-fill to last_updated (skip if missing with informative message)
    df_working = impute_forward_fill(df_working, ["last_updated"])

    # 7. Generate imputation decisions JSON
    decisions = document_imputation_decisions(df_raw, df_working)

    # 8. Validate before/after metrics
    df_validation = validate_imputation(df_raw, df_working)

    # 9. Save cleaned dataset
    processed_dir = "data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    processed_path = os.path.join(processed_dir, "cleaned_data.csv")
    df_working.to_csv(processed_path, index=False)
    print(f"\nCleaned dataset successfully saved to {processed_path}")

    # 10. Print final success message
    print("\nMissing value handling pipeline executed successfully!")
