"""
Dataset Intake & Source Validation Script

This script validates incoming datasets before they enter the processing pipeline.
It checks file existence, format, schema, encoding, and collects dataset statistics.
"""

import os
import json
import pandas as pd
import chardet
from datetime import datetime
from pathlib import Path


def validate_file_exists(filepath):
    """
    Check whether the file exists and is not empty.
    
    Args:
        filepath (str): Path to the file to validate
        
    Returns:
        dict: Validation result with pass/fail status and message
    """
    result = {
        "check": "file_existence",
        "filepath": filepath,
        "passed": False,
        "message": ""
    }
    
    if not os.path.exists(filepath):
        result["message"] = f"File does not exist: {filepath}"
        return result
    
    if os.path.getsize(filepath) == 0:
        result["message"] = f"File is empty: {filepath}"
        return result
    
    result["passed"] = True
    result["message"] = f"File exists and is not empty: {filepath}"
    return result


def validate_file_format(filepath, allowed_formats=['csv', 'json', 'xlsx']):
    """
    Validate the file extension against allowed formats.
    
    Args:
        filepath (str): Path to the file to validate
        allowed_formats (list): List of allowed file extensions
        
    Returns:
        dict: Validation result with pass/fail status and message
    """
    result = {
        "check": "file_format",
        "filepath": filepath,
        "allowed_formats": allowed_formats,
        "detected_format": None,
        "passed": False,
        "message": ""
    }
    
    file_ext = Path(filepath).suffix.lower().lstrip('.')
    
    if not file_ext:
        result["message"] = "File has no extension"
        return result
    
    result["detected_format"] = file_ext
    
    if file_ext not in allowed_formats:
        result["message"] = f"Unsupported format '{file_ext}'. Allowed formats: {', '.join(allowed_formats)}"
        return result
    
    result["passed"] = True
    result["message"] = f"File format '{file_ext}' is supported"
    return result


def validate_schema(df, expected_columns):
    """
    Compare dataset columns against the expected schema.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        expected_columns (list): List of expected column names
        
    Returns:
        dict: Validation result with missing/unexpected columns
    """
    result = {
        "check": "schema_validation",
        "expected_columns": expected_columns,
        "actual_columns": list(df.columns),
        "missing_columns": [],
        "unexpected_columns": [],
        "passed": False,
        "message": ""
    }
    
    actual_columns = set(df.columns)
    expected_set = set(expected_columns)
    
    missing_columns = expected_set - actual_columns
    unexpected_columns = actual_columns - expected_set
    
    result["missing_columns"] = list(missing_columns)
    result["unexpected_columns"] = list(unexpected_columns)
    
    if missing_columns or unexpected_columns:
        issues = []
        if missing_columns:
            issues.append(f"Missing columns: {', '.join(missing_columns)}")
        if unexpected_columns:
            issues.append(f"Unexpected columns: {', '.join(unexpected_columns)}")
        result["message"] = "; ".join(issues)
        return result
    
    result["passed"] = True
    result["message"] = "Schema validation passed - all expected columns present"
    return result


def detect_encoding(filepath):
    """
    Detect the file encoding using chardet.
    
    Args:
        filepath (str): Path to the file to analyze
        
    Returns:
        dict: Encoding detection result with encoding and confidence
    """
    result = {
        "check": "encoding_detection",
        "filepath": filepath,
        "encoding": None,
        "confidence": None,
        "message": ""
    }
    
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read(1024)  # Read first 1KB for detection
            detection = chardet.detect(raw_data)
            
        result["encoding"] = detection.get('encoding')
        result["confidence"] = round(detection.get('confidence', 0) * 100, 2)
        result["message"] = f"Detected encoding: {result['encoding']} (confidence: {result['confidence']}%)"
        result["passed"] = True
        
    except Exception as e:
        result["message"] = f"Error detecting encoding: {str(e)}"
        result["passed"] = False
    
    return result


def capture_dataset_stats(filepath, df):
    """
    Capture dataset statistics including dimensions and file size.
    
    Args:
        filepath (str): Path to the file
        df (pd.DataFrame): DataFrame containing the data
        
    Returns:
        dict: Dataset statistics
    """
    file_size_bytes = os.path.getsize(filepath)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 4)
    
    result = {
        "check": "dataset_statistics",
        "filepath": filepath,
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "file_size_bytes": file_size_bytes,
        "file_size_mb": file_size_mb,
        "message": f"Dataset contains {len(df)} rows and {len(df.columns)} columns ({file_size_mb} MB)",
        "passed": True
    }
    
    return result


def generate_intake_report(filepath, expected_columns):
    """
    Generate a comprehensive intake report with all validation results.
    
    Args:
        filepath (str): Path to the file to validate
        expected_columns (list): Expected column names for schema validation
        
    Returns:
        dict: Complete intake report with all validation results
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "filepath": filepath,
        "expected_columns": expected_columns,
        "validation_results": [],
        "overall_status": "FAILED",
        "summary": ""
    }
    
    # Step 1: File existence validation
    existence_result = validate_file_exists(filepath)
    report["validation_results"].append(existence_result)
    
    if not existence_result["passed"]:
        report["overall_status"] = "FAILED"
        report["summary"] = "Validation failed: File does not exist or is empty"
        return report
    
    # Step 2: File format validation
    format_result = validate_file_format(filepath)
    report["validation_results"].append(format_result)
    
    if not format_result["passed"]:
        report["overall_status"] = "FAILED"
        report["summary"] = "Validation failed: Unsupported file format"
        return report
    
    # Step 3: Load data based on format
    try:
        if format_result["detected_format"] == 'csv':
            df = pd.read_csv(filepath)
        elif format_result["detected_format"] == 'json':
            df = pd.read_json(filepath)
        elif format_result["detected_format"] == 'xlsx':
            df = pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported format: {format_result['detected_format']}")
    except Exception as e:
        error_result = {
            "check": "data_loading",
            "passed": False,
            "message": f"Error loading data: {str(e)}"
        }
        report["validation_results"].append(error_result)
        report["overall_status"] = "FAILED"
        report["summary"] = f"Validation failed: Could not load data - {str(e)}"
        return report
    
    # Step 4: Schema validation
    schema_result = validate_schema(df, expected_columns)
    report["validation_results"].append(schema_result)
    
    # Step 5: Encoding detection
    encoding_result = detect_encoding(filepath)
    report["validation_results"].append(encoding_result)
    
    # Step 6: Dataset statistics
    stats_result = capture_dataset_stats(filepath, df)
    report["validation_results"].append(stats_result)
    
    # Determine overall status
    all_passed = all(result.get("passed", True) for result in report["validation_results"])
    report["overall_status"] = "PASSED" if all_passed else "FAILED"
    
    # Generate summary
    passed_count = sum(1 for r in report["validation_results"] if r.get("passed", False))
    total_count = len(report["validation_results"])
    
    if all_passed:
        report["summary"] = f"All validations passed ({passed_count}/{total_count} checks)"
    else:
        failed_checks = [r["check"] for r in report["validation_results"] if not r.get("passed", False)]
        report["summary"] = f"Validation failed: {', '.join(failed_checks)} ({passed_count}/{total_count} checks passed)"
    
    return report


def main():
    """Main execution function."""
    # Configuration
    sample_file = "data/raw/sample.csv"
    expected_columns = ["customer_id", "customer_name", "transaction_amount", "transaction_date"]
    output_report = "output/intake_report.json"
    
    print(f"Starting validation for: {sample_file}")
    print(f"Expected columns: {expected_columns}")
    print("-" * 50)
    
    # Generate intake report
    report = generate_intake_report(sample_file, expected_columns)
    
    # Print results
    print(f"Overall Status: {report['overall_status']}")
    print(f"Summary: {report['summary']}")
    print("\nValidation Results:")
    for result in report["validation_results"]:
        status = "✓" if result.get("passed", False) else "✗"
        print(f"  {status} {result['check']}: {result.get('message', 'No message')}")
    
    # Save report to JSON
    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    with open(output_report, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {output_report}")
    
    return report["overall_status"] == "PASSED"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
