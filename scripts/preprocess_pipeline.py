"""
Data Preprocessing Pipeline

This script orchestrates the complete data preprocessing workflow for OnboardIQ datasets.
It integrates type enforcement with existing validation and profiling to create a unified
preprocessing pipeline that prepares data for analysis and model training.
"""

import os
import pandas as pd
from type_enforcement import enforce_types, generate_conversion_report
from validate_intake import validate_file_exists, validate_file_format, validate_schema
import json
from datetime import datetime


def preprocess_dataset(
    filepath: str,
    expected_columns: list = None,
    type_schema: dict = None,
    auto_detect_types: bool = True
) -> tuple:
    """
    Complete preprocessing pipeline for a single dataset.
    
    Steps:
    1. Validate file existence and format
    2. Validate schema if expected columns provided
    3. Load the dataset
    4. Enforce data types
    5. Generate conversion report
    6. Return processed DataFrame and reports
    
    Args:
        filepath: Path to the dataset file
        expected_columns: Optional list of expected column names for schema validation
        type_schema: Optional dictionary mapping column names to target types
        auto_detect_types: Whether to auto-detect types if schema not provided
    
    Returns:
        Tuple of (processed DataFrame, validation report, conversion report)
    """
    print(f"\n{'='*70}")
    print(f"PREPROCESSING PIPELINE: {os.path.basename(filepath)}")
    print(f"{'='*70}")
    
    # Step 1: File existence validation
    print("\n[1/5] Validating file existence...")
    existence_check = validate_file_exists(filepath)
    print(f"  Status: {'PASS' if existence_check['passed'] else 'FAIL'}")
    print(f"  Message: {existence_check['message']}")
    
    if not existence_check['passed']:
        raise FileNotFoundError(existence_check['message'])
    
    # Step 2: File format validation
    print("\n[2/5] Validating file format...")
    format_check = validate_file_format(filepath)
    print(f"  Status: {'PASS' if format_check['passed'] else 'FAIL'}")
    print(f"  Message: {format_check['message']}")
    
    if not format_check['passed']:
        raise ValueError(format_check['message'])
    
    # Step 3: Load dataset
    print("\n[3/5] Loading dataset...")
    try:
        if format_check['detected_format'] == 'csv':
            df = pd.read_csv(filepath)
        elif format_check['detected_format'] == 'json':
            df = pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported format: {format_check['detected_format']}")
        
        print(f"  Loaded: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        raise Exception(f"Error loading dataset: {str(e)}")
    
    # Step 4: Schema validation (if expected columns provided)
    validation_report = {
        'filepath': filepath,
        'existence_check': existence_check,
        'format_check': format_check,
        'schema_check': None
    }
    
    if expected_columns:
        print("\n[4/5] Validating schema...")
        schema_check = validate_schema(df, expected_columns)
        validation_report['schema_check'] = schema_check
        print(f"  Status: {'PASS' if schema_check['passed'] else 'FAIL'}")
        print(f"  Message: {schema_check['message']}")
        
        if not schema_check['passed']:
            print(f"  Warning: Schema validation failed but continuing...")
    else:
        print("\n[4/5] Schema validation skipped (no expected columns provided)")
    
    # Step 5: Type enforcement
    print("\n[5/5] Enforcing data types...")
    df_before = df.copy()
    df_processed, conversion_report = enforce_types(
        df,
        type_schema=type_schema,
        auto_detect=auto_detect_types
    )
    
    print(f"  Status: {conversion_report['overall_status']}")
    print(f"  Shape: {conversion_report['original_shape']} → {conversion_report['final_shape']}")
    
    # Print conversion summary
    for conv in conversion_report['column_conversions']:
        if conv['converted']:
            print(f"    ✓ {conv['column']}: {conv['original_type']} → {conv['new_type']}")
        elif conv['warnings']:
            print(f"    ✗ {conv['column']}: {', '.join(conv['warnings'][:1])}")
    
    # Generate human-readable report
    print("\n" + generate_conversion_report(df_before, df_processed, conversion_report))
    
    return df_processed, validation_report, conversion_report


def preprocess_onboardiq_datasets() -> dict:
    """
    Preprocess all OnboardIQ datasets with their specific schemas.
    
    Returns:
        Dictionary containing processed DataFrames and reports for all datasets
    """
    # Define dataset configurations
    datasets = {
        'employees': {
            'filepath': 'data/employees.csv',
            'expected_columns': ['ID', 'Name', 'Department', 'Joining Date'],
            'type_schema': {
                'ID': 'numeric',
                'Name': 'keep',
                'Department': 'categorical',
                'Joining Date': 'datetime'
            }
        },
        'onboarding': {
            'filepath': 'data/onboarding.csv',
            'expected_columns': ['Employee ID', 'Laptop Issued', 'Training Completed', 
                                'Security Access Granted', 'Email Setup', 'Onboarding Complete'],
            'type_schema': {
                'Employee ID': 'numeric',
                'Laptop Issued': 'boolean',
                'Training Completed': 'boolean',
                'Security Access Granted': 'boolean',
                'Email Setup': 'boolean',
                'Onboarding Complete': 'boolean'
            }
        },
        'tools': {
            'filepath': 'data/tools.csv',
            'expected_columns': ['Employee ID', 'Slack Messages', 'GitHub Commits', 
                                'Jira Tickets Resolved', 'Slack Reactions', 'GitHub PRs Reviewed'],
            'type_schema': {
                'Employee ID': 'numeric',
                'Slack Messages': 'numeric',
                'GitHub Commits': 'numeric',
                'Jira Tickets Resolved': 'numeric',
                'Slack Reactions': 'numeric',
                'GitHub PRs Reviewed': 'numeric'
            }
        },
        'support': {
            'filepath': 'data/support.csv',
            'expected_columns': ['Ticket ID', 'Employee ID', 'Issue Type', 
                                'Resolution Time (hours)', 'Status', 'Priority'],
            'type_schema': {
                'Ticket ID': 'keep',
                'Employee ID': 'numeric',
                'Issue Type': 'categorical',
                'Resolution Time (hours)': 'numeric',
                'Status': 'categorical',
                'Priority': 'categorical'
            }
        }
    }
    
    results = {}
    
    for dataset_name, config in datasets.items():
        try:
            print(f"\n{'#'*70}")
            print(f"# PROCESSING DATASET: {dataset_name.upper()}")
            print(f"{'#'*70}")
            
            df_processed, validation_report, conversion_report = preprocess_dataset(
                filepath=config['filepath'],
                expected_columns=config['expected_columns'],
                type_schema=config['type_schema'],
                auto_detect_types=False
            )
            
            results[dataset_name] = {
                'dataframe': df_processed,
                'validation_report': validation_report,
                'conversion_report': conversion_report,
                'status': 'SUCCESS'
            }
            
        except Exception as e:
            print(f"\nERROR processing {dataset_name}: {str(e)}")
            results[dataset_name] = {
                'dataframe': None,
                'validation_report': None,
                'conversion_report': None,
                'status': 'FAILED',
                'error': str(e)
            }
    
    return results


def save_processed_datasets(results: dict, output_dir: str = 'data/processed') -> None:
    """
    Save processed datasets to the output directory.
    
    Args:
        results: Dictionary of processed datasets from preprocess_onboardiq_datasets
        output_dir: Directory to save processed files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*70}")
    print("SAVING PROCESSED DATASETS")
    print(f"{'='*70}")
    
    for dataset_name, result in results.items():
        if result['status'] == 'SUCCESS' and result['dataframe'] is not None:
            output_path = os.path.join(output_dir, f"{dataset_name}_processed.csv")
            result['dataframe'].to_csv(output_path, index=False)
            print(f"✓ Saved: {output_path}")
        else:
            print(f"✗ Skipped: {dataset_name} (processing failed)")
    
    print(f"{'='*70}")


def generate_pipeline_summary(results: dict, output_path: str = 'output/preprocessing_summary.json') -> dict:
    """
    Generate a summary report of the entire preprocessing pipeline.
    
    Args:
        results: Dictionary of processed datasets
        output_path: Path to save the summary report
    
    Returns:
        Summary dictionary
    """
    summary = {
        'timestamp': datetime.now().isoformat(),
        'pipeline_status': 'SUCCESS',
        'datasets_processed': len(results),
        'datasets_successful': 0,
        'datasets_failed': 0,
        'dataset_details': {}
    }
    
    for dataset_name, result in results.items():
        if result['status'] == 'SUCCESS':
            summary['datasets_successful'] += 1
            summary['dataset_details'][dataset_name] = {
                'status': 'SUCCESS',
                'rows': len(result['dataframe']),
                'columns': len(result['dataframe'].columns),
                'conversion_status': result['conversion_report']['overall_status'],
                'columns_converted': sum(1 for c in result['conversion_report']['column_conversions'] if c['converted'])
            }
        else:
            summary['datasets_failed'] += 1
            summary['pipeline_status'] = 'PARTIAL'
            summary['dataset_details'][dataset_name] = {
                'status': 'FAILED',
                'error': result.get('error', 'Unknown error')
            }
    
    # Save summary
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n{'='*70}")
    print("PIPELINE SUMMARY")
    print(f"{'='*70}")
    print(f"Timestamp: {summary['timestamp']}")
    print(f"Overall Status: {summary['pipeline_status']}")
    print(f"Datasets Processed: {summary['datasets_processed']}")
    print(f"Successful: {summary['datasets_successful']}")
    print(f"Failed: {summary['datasets_failed']}")
    print(f"Summary saved to: {output_path}")
    print(f"{'='*70}")
    
    return summary


if __name__ == "__main__":
    print("="*70)
    print("ONBOARDIQ DATA PREPROCESSING PIPELINE")
    print("="*70)
    print("Starting preprocessing workflow...")
    
    # Process all datasets
    results = preprocess_onboardiq_datasets()
    
    # Save processed datasets
    save_processed_datasets(results)
    
    # Generate summary report
    summary = generate_pipeline_summary(results)
    
    # Final status
    print("\n" + "="*70)
    if summary['pipeline_status'] == 'SUCCESS':
        print("PIPELINE COMPLETED SUCCESSFULLY")
    else:
        print("PIPELINE COMPLETED WITH ERRORS")
    print("="*70)
