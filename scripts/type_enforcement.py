"""
Data Type Enforcement & Standardisation Module

This module provides functions for enforcing and standardising data types
in DataFrames before analysis, feature engineering, or model training.
It handles date/time conversion, numeric cleaning, currency handling,
boolean detection, and categorical conversion with comprehensive reporting.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import re


def convert_to_datetime(
    column: pd.Series,
    formats: Optional[List[str]] = None
) -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Convert a column to datetime with multiple format support.
    
    Args:
        column: Pandas Series to convert
        formats: List of datetime formats to try (default: common formats)
    
    Returns:
        Tuple of (converted series, conversion metadata)
    """
    if formats is None:
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%d-%m-%Y',
            '%m-%d-%Y',
            '%Y%m%d'
        ]
    
    metadata = {
        'original_type': str(column.dtype),
        'converted': False,
        'failed_count': 0,
        'format_used': None,
        'warnings': []
    }
    
    # Skip if already datetime
    if pd.api.types.is_datetime64_any_dtype(column):
        metadata['converted'] = False
        metadata['warnings'].append('Column already datetime')
        return column, metadata
    
    # Try each format
    for fmt in formats:
        try:
            converted = pd.to_datetime(column, format=fmt, errors='coerce')
            failed_count = converted.isna().sum()
            
            # Check if conversion was successful (most values converted)
            success_rate = 1 - (failed_count / len(column))
            
            if success_rate >= 0.8:  # 80% success threshold
                metadata['converted'] = True
                metadata['failed_count'] = int(failed_count)
                metadata['format_used'] = fmt
                
                if failed_count > 0:
                    metadata['warnings'].append(
                        f'{failed_count} values could not be converted with format {fmt}'
                    )
                
                return converted, metadata
        except Exception:
            continue
    
    # If no format worked, try pandas automatic detection
    try:
        converted = pd.to_datetime(column, errors='coerce')
        failed_count = converted.isna().sum()
        success_rate = 1 - (failed_count / len(column))
        
        if success_rate >= 0.5:
            metadata['converted'] = True
            metadata['failed_count'] = int(failed_count)
            metadata['format_used'] = 'auto'
            
            if failed_count > 0:
                metadata['warnings'].append(
                    f'{failed_count} values could not be converted (auto detection)'
                )
            
            return converted, metadata
    except Exception as e:
        metadata['warnings'].append(f'Auto detection failed: {str(e)}')
    
    metadata['warnings'].append('Could not convert to datetime with any format')
    return column, metadata


def convert_to_numeric(
    column: pd.Series,
    handle_currency: bool = True
) -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Convert a column to numeric, handling currency symbols and formatting.
    
    Args:
        column: Pandas Series to convert
        handle_currency: Whether to remove currency symbols
    
    Returns:
        Tuple of (converted series, conversion metadata)
    """
    metadata = {
        'original_type': str(column.dtype),
        'converted': False,
        'failed_count': 0,
        'warnings': []
    }
    
    # Skip if already numeric
    if pd.api.types.is_numeric_dtype(column):
        metadata['converted'] = False
        metadata['warnings'].append('Column already numeric')
        return column, metadata
    
    # Make a copy for conversion
    column_copy = column.copy()
    
    # Handle currency symbols if enabled
    if handle_currency:
        # Remove common currency symbols
        currency_symbols = ['$', '€', '£', '₹', '¥', '₽']
        for symbol in currency_symbols:
            column_copy = column_copy.astype(str).str.replace(symbol, '', regex=False)
        
        # Remove commas and spaces
        column_copy = column_copy.astype(str).str.replace(',', '', regex=False)
        column_copy = column_copy.astype(str).str.replace(' ', '', regex=False)
    
    # Attempt conversion
    try:
        converted = pd.to_numeric(column_copy, errors='coerce')
        failed_count = converted.isna().sum()
        success_rate = 1 - (failed_count / len(column))
        
        if success_rate >= 0.8:
            metadata['converted'] = True
            metadata['failed_count'] = int(failed_count)
            
            if failed_count > 0:
                metadata['warnings'].append(
                    f'{failed_count} values could not be converted to numeric'
                )
            
            return converted, metadata
        else:
            metadata['warnings'].append(
                f'Conversion success rate {success_rate:.1%} below threshold'
            )
    except Exception as e:
        metadata['warnings'].append(f'Numeric conversion failed: {str(e)}')
    
    return column, metadata


def convert_to_boolean(column: pd.Series) -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Convert a column to boolean, detecting various boolean representations.
    
    Handles: True/False, Yes/No, Y/N, T/F, 0/1, etc.
    
    Args:
        column: Pandas Series to convert
    
    Returns:
        Tuple of (converted series, conversion metadata)
    """
    metadata = {
        'original_type': str(column.dtype),
        'converted': False,
        'failed_count': 0,
        'warnings': []
    }
    
    # Skip if already boolean
    if pd.api.types.is_bool_dtype(column):
        metadata['converted'] = False
        metadata['warnings'].append('Column already boolean')
        return column, metadata
    
    # Create mapping for boolean representations
    bool_mapping = {
        # Standard
        'true': True, 'false': False,
        'yes': True, 'no': False,
        'y': True, 'n': False,
        't': True, 'f': False,
        # Case insensitive
        'True': True, 'False': False,
        'Yes': True, 'No': False,
        'Y': True, 'N': False,
        'T': True, 'F': False,
        'YES': True, 'NO': False,
        # Numeric
        '1': True, '0': False,
        1: True, 0: False
    }
    
    # Convert to lowercase string for comparison
    column_str = column.astype(str).str.lower().str.strip()
    
    # Apply mapping
    converted = column_str.map(bool_mapping)
    
    # Check conversion success
    failed_count = converted.isna().sum()
    success_rate = 1 - (failed_count / len(column))
    
    if success_rate >= 0.8:
        metadata['converted'] = True
        metadata['failed_count'] = int(failed_count)
        
        if failed_count > 0:
            metadata['warnings'].append(
                f'{failed_count} values could not be converted to boolean'
            )
        
        return converted, metadata
    else:
        metadata['warnings'].append(
            f'Conversion success rate {success_rate:.1%} below threshold'
        )
    
    return column, metadata


def convert_to_categorical(
    df: pd.DataFrame,
    columns: List[str],
    threshold: float = 0.5
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Convert specified columns to categorical dtype if they have low cardinality.
    
    Args:
        df: DataFrame to modify
        columns: List of column names to consider for conversion
        threshold: Maximum unique ratio (unique/total) to convert to categorical
    
    Returns:
        Tuple of (modified DataFrame, conversion metadata)
    """
    metadata = {
        'converted_columns': [],
        'skipped_columns': [],
        'warnings': []
    }
    
    for col in columns:
        if col not in df.columns:
            metadata['warnings'].append(f'Column {col} not found in DataFrame')
            continue
        
        # Skip if already categorical
        if pd.api.types.is_categorical_dtype(df[col]):
            metadata['skipped_columns'].append(col)
            continue
        
        # Calculate cardinality ratio
        unique_count = df[col].nunique()
        total_count = len(df)
        unique_ratio = unique_count / total_count
        
        # Convert if cardinality is low enough
        if unique_ratio <= threshold:
            df[col] = df[col].astype('category')
            metadata['converted_columns'].append({
                'column': col,
                'unique_count': unique_count,
                'total_count': total_count,
                'unique_ratio': round(unique_ratio, 3)
            })
        else:
            metadata['skipped_columns'].append(col)
    
    return df, metadata


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Automatically detect appropriate data types for DataFrame columns.
    
    Args:
        df: DataFrame to analyze
    
    Returns:
        Dictionary mapping column names to detected types
    """
    detected_types = {}
    
    for col in df.columns:
        col_lower = col.lower()
        dtype = str(df[col].dtype)
        
        # Date/time detection by column name patterns
        if any(keyword in col_lower for keyword in 
               ['date', 'time', 'joined', 'created', 'updated', 'timestamp']):
            detected_types[col] = 'datetime'
        
        # ID detection
        elif 'id' in col_lower and dtype == 'object':
            detected_types[col] = 'numeric'
        
        # Currency detection (amount, price, cost, revenue)
        elif any(keyword in col_lower for keyword in 
               ['amount', 'price', 'cost', 'revenue', 'salary', 'budget']):
            detected_types[col] = 'currency'
        
        # Boolean detection by column name
        elif any(keyword in col_lower for keyword in 
               ['is_', 'has_', 'issued', 'completed', 'granted', 'setup']):
            detected_types[col] = 'boolean'
        
        # Status/priority/type detection (likely categorical)
        elif any(keyword in col_lower for keyword in 
               ['status', 'priority', 'type', 'department', 'category']):
            detected_types[col] = 'categorical'
        
        # Count/numeric detection
        elif any(keyword in col_lower for keyword in 
               ['count', 'messages', 'commits', 'tickets', 'reactions', 'time']):
            detected_types[col] = 'numeric'
        
        # Default: keep as is
        else:
            detected_types[col] = 'keep'
    
    return detected_types


def enforce_types(
    df: pd.DataFrame,
    type_schema: Optional[Dict[str, str]] = None,
    auto_detect: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Enforce data types on DataFrame columns.
    
    Args:
        df: DataFrame to process
        type_schema: Optional dictionary mapping column names to target types
                    (datetime, numeric, currency, boolean, categorical, keep)
        auto_detect: Whether to automatically detect types if schema not provided
    
    Returns:
        Tuple of (type-enforced DataFrame, conversion report)
    """
    df_copy = df.copy()
    conversion_report = {
        'timestamp': datetime.now().isoformat(),
        'original_shape': df.shape,
        'final_shape': None,
        'column_conversions': [],
        'overall_status': 'SUCCESS',
        'warnings': []
    }
    
    # Determine type schema
    if type_schema is None and auto_detect:
        type_schema = detect_column_types(df_copy)
    elif type_schema is None:
        type_schema = {col: 'keep' for col in df_copy.columns}
    
    # Apply type conversions
    for col, target_type in type_schema.items():
        if col not in df_copy.columns:
            conversion_report['warnings'].append(
                f'Column {col} in schema not found in DataFrame'
            )
            continue
        
        if target_type == 'keep':
            continue
        
        original_dtype = str(df_copy[col].dtype)
        conversion_metadata = {
            'column': col,
            'original_type': original_dtype,
            'target_type': target_type,
            'new_type': original_dtype,
            'converted': False,
            'failed_count': 0,
            'warnings': []
        }
        
        try:
            if target_type == 'datetime':
                df_copy[col], meta = convert_to_datetime(df_copy[col])
                conversion_metadata.update(meta)
            
            elif target_type in ['numeric', 'currency']:
                df_copy[col], meta = convert_to_numeric(
                    df_copy[col], 
                    handle_currency=(target_type == 'currency')
                )
                conversion_metadata.update(meta)
            
            elif target_type == 'boolean':
                df_copy[col], meta = convert_to_boolean(df_copy[col])
                conversion_metadata.update(meta)
            
            elif target_type == 'categorical':
                df_copy, meta = convert_to_categorical(df_copy, [col])
                conversion_metadata['converted'] = col in meta.get('converted_columns', [])
                conversion_metadata['warnings'].extend(meta.get('warnings', []))
            
            conversion_metadata['new_type'] = str(df_copy[col].dtype)
            
        except Exception as e:
            conversion_metadata['warnings'].append(f'Conversion error: {str(e)}')
            conversion_report['overall_status'] = 'PARTIAL'
        
        conversion_report['column_conversions'].append(conversion_metadata)
    
    conversion_report['final_shape'] = df_copy.shape
    
    # Check if any conversions failed
    failed_conversions = [
        c for c in conversion_report['column_conversions']
        if c['warnings'] and not c['converted']
    ]
    
    if failed_conversions:
        conversion_report['overall_status'] = 'PARTIAL'
    
    return df_copy, conversion_report


def generate_conversion_report(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    conversion_report: Dict[str, Any]
) -> str:
    """
    Generate a human-readable conversion report.
    
    Args:
        df_before: DataFrame before conversion
        df_after: DataFrame after conversion
        conversion_report: Conversion metadata from enforce_types
    
    Returns:
        Formatted report string
    """
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("DATA TYPE CONVERSION REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"Timestamp: {conversion_report['timestamp']}")
    report_lines.append(f"Shape: {conversion_report['original_shape']} → {conversion_report['final_shape']}")
    report_lines.append(f"Overall Status: {conversion_report['overall_status']}")
    report_lines.append("")
    
    # Column conversions
    report_lines.append("COLUMN CONVERSIONS:")
    report_lines.append("-" * 70)
    
    for conv in conversion_report['column_conversions']:
        status = "✓" if conv['converted'] else "✗"
        report_lines.append(
            f"{status} {conv['column']}: {conv['original_type']} → {conv['new_type']} "
            f"({conv['target_type']})"
        )
        
        if conv['failed_count'] > 0:
            report_lines.append(f"    Failed conversions: {conv['failed_count']}")
        
        for warning in conv['warnings']:
            report_lines.append(f"    Warning: {warning}")
    
    # Overall warnings
    if conversion_report['warnings']:
        report_lines.append("")
        report_lines.append("OVERALL WARNINGS:")
        report_lines.append("-" * 70)
        for warning in conversion_report['warnings']:
            report_lines.append(f"  - {warning}")
    
    report_lines.append("=" * 70)
    
    return "\n".join(report_lines)


if __name__ == "__main__":
    # Example usage
    print("Type Enforcement Module - Use as library")
    print("Import functions: enforce_types, generate_conversion_report")
