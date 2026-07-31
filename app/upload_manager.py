import os
import shutil
import json
import traceback
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Employee
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing validation/preprocessing scripts
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.validate_intake import validate_file_exists, validate_file_format, detect_encoding
from scripts.profile_data import profile_nulls_and_duplicates, identify_quality_issues
from scripts.handle_missing import analyze_missing_values
from scripts.type_enforcement import enforce_types
from scripts.onboarding_quality import (
    process_employee_dataframe,
    save_quality_report,
    calculate_kpis,
)

UPLOAD_DIR = Path("uploads")
METADATA_FILE = UPLOAD_DIR / "metadata.json"


def get_user_upload_dir(user_id: int) -> Path:
    """Get user-specific upload directory."""
    user_dir = UPLOAD_DIR / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_user_metadata_file(user_id: int) -> Path:
    """Get user-specific metadata file."""
    return get_user_upload_dir(user_id) / "metadata.json"


def _optional_value(row, column):
    """Return a clean optional string value for a CSV field."""
    value = row.get(column)
    return None if value is None or pd.isna(value) else str(value)


def init_upload_dir():
    """Ensure upload directory exists."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_upload_status(user_id: int = None) -> dict:
    """Returns the current upload status from user-specific metadata.json."""
    if user_id:
        metadata_file = get_user_metadata_file(user_id)
    else:
        metadata_file = METADATA_FILE
    
    if metadata_file.exists():
        try:
            with open(metadata_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "status": "idle",
        "active_file": None,
        "rows": 0,
        "columns": 0,
        "upload_time": None,
        "validation_passed": False,
        "processing_time_ms": 0
    }

def save_upload_status(status_dict: dict, user_id: int = None):
    """Saves the upload status to user-specific metadata.json."""
    if user_id:
        metadata_file = get_user_metadata_file(user_id)
    else:
        metadata_file = METADATA_FILE
    
    with open(metadata_file, "w") as f:
        json.dump(status_dict, f, indent=2)

def clean_processed_dir():
    """Backup processed files if they are the original synthetic ones."""
    # We don't need active backup because we can restore by regenerating synthetic data
    pass

def restore_synthetic_data(user_id: int = None):
    """Remove the active upload and return the application to an empty state."""
    db = SessionLocal()
    try:
        if user_id:
            db.query(Employee).filter(Employee.user_id == user_id).delete()
        else:
            db.query(Employee).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error clearing employee DB: {e}")
    finally:
        db.close()

    # Keep any local processing files out of the active application state.
    # Dashboard endpoints only read processed data when an upload is active.
    save_upload_status({
        "status": "idle",
        "active_file": None,
        "rows": 0,
        "columns": 0,
        "upload_time": None,
        "validation_passed": False,
        "processing_time_ms": 0
    }, user_id=user_id)

def process_and_validate_upload(filepath: str, user_id: int = None) -> dict:
    """
    Loads, validates, and processes the uploaded employee dataset.
    Integrates existing scripts: validate_intake, profile_data, handle_missing, type_enforcement.
    Returns:
        Dict report with status and details
    """
    start_time = datetime.now()
    report = {
        "passed": False,
        "error": None,
        "rows": 0,
        "columns": 0,
        "filename": os.path.basename(filepath),
        "issues": []
    }

    # 1. Validate file existence (from validate_intake)
    existence = validate_file_exists(filepath)
    if not existence["passed"]:
        report["error"] = existence["message"]
        return report

    # 2. Validate format (from validate_intake)
    fmt_check = validate_file_format(filepath, allowed_formats=['csv', 'xlsx'])
    if not fmt_check["passed"]:
        report["error"] = "Unsupported file type"
        report["issues"].append(fmt_check["message"])
        return report

    file_ext = fmt_check["detected_format"]

    # 3. Load using pandas and catch corruption
    try:
        if file_ext == 'csv':
            # Detect encoding
            enc_check = detect_encoding(filepath)
            encoding = enc_check.get("encoding", "utf-8")
            df = pd.read_csv(filepath, encoding=encoding)
        else:
            df = pd.read_excel(filepath)
    except Exception as e:
        report["error"] = "Corrupted file"
        report["issues"].append(f"Failed to read file contents: {str(e)}")
        return report

    # Check empty file
    if df.empty:
        report["error"] = "Corrupted file"
        report["issues"].append("The uploaded dataset contains zero rows.")
        return report

    # 4. Map columns to expected system formats dynamically
    column_mapping = {}
    for col in df.columns:
        norm = str(col).strip().lower().replace(" ", "_")
        if norm in ['id', 'employee_id', 'employee id']:
            column_mapping[col] = 'employee_id'
        elif norm in ['name', 'employee_name', 'employee name']:
            column_mapping[col] = 'employee_name'
        elif norm in ['joining_date', 'joining date']:
            column_mapping[col] = 'joining_date'
        elif norm in ['laptop_issued', 'laptop issued']:
            column_mapping[col] = 'laptop_issued'
        elif norm in ['access_granted', 'security_access_granted', 'security access granted', 'access granted']:
            column_mapping[col] = 'access_granted'
        elif norm in ['training_completed', 'training completed']:
            column_mapping[col] = 'training_completed'
        elif norm in ['email_setup', 'email setup']:
            column_mapping[col] = 'email_setup'
        elif norm in ['onboarding_complete', 'onboarding complete']:
            column_mapping[col] = 'onboarding_complete'
        elif norm in ['department']:
            column_mapping[col] = 'department'
        elif norm in ['github_username', 'github username']:
            column_mapping[col] = 'github_username'
        elif norm in ['slack_id', 'slack id']:
            column_mapping[col] = 'slack_id'
        elif norm in ['jira_id', 'jira id']:
            column_mapping[col] = 'jira_id'
        elif norm in ['slack_messages', 'slack messages']:
            column_mapping[col] = 'slack_messages'
        elif norm in ['github_commits', 'github commits']:
            column_mapping[col] = 'github_commits'
        elif norm in ['jira_tickets_resolved', 'jira tickets resolved']:
            column_mapping[col] = 'jira_tickets_resolved'
        elif norm in ['slack_reactions', 'slack reactions']:
            column_mapping[col] = 'slack_reactions'
        elif norm in ['github_prs_reviewed', 'github prs reviewed', 'github_pr_reviewed']:
            column_mapping[col] = 'github_prs_reviewed'
        elif norm in ['laptop_issued_date', 'laptop issued date']:
            column_mapping[col] = 'laptop_issued_date'
        elif norm in ['email_setup_date', 'email setup date']:
            column_mapping[col] = 'email_setup_date'
        elif norm in ['access_granted_date', 'access granted date', 'security_access_granted_date']:
            column_mapping[col] = 'access_granted_date'
        elif norm in ['training_completed_date', 'training completed date']:
            column_mapping[col] = 'training_completed_date'
        elif norm in ['onboarding_complete_date', 'onboarding complete date']:
            column_mapping[col] = 'onboarding_complete_date'
        else:
            column_mapping[col] = norm

    df_mapped = df.rename(columns=column_mapping)

    # 5. Required columns check
    required_cols = ['employee_id', 'employee_name']
    missing_required = [col for col in required_cols if col not in df_mapped.columns]
    if missing_required:
        report["error"] = "Missing required columns"
        report["issues"].append(f"Missing required identifier columns: {', '.join(missing_required)}")
        return report

    # Ensure employee_id has no nulls
    if df_mapped['employee_id'].isnull().any():
        report["error"] = "Missing values"
        report["issues"].append("employee_id column contains null/missing values.")
        return report

    # 6. Check duplicate IDs
    if df_mapped['employee_id'].duplicated().any():
        report["error"] = "Duplicate employee IDs"
        dup_ids = df_mapped['employee_id'][df_mapped['employee_id'].duplicated()].unique()
        report["issues"].append(f"Duplicate Employee IDs found: {list(dup_ids[:5])}")
        return report

    # 7. Check joining date format
    if 'joining_date' in df_mapped.columns:
        # Validate that dates can be parsed
        parsed_dates = pd.to_datetime(df_mapped['joining_date'], errors='coerce')
        if parsed_dates.isnull().any():
            invalid_count = parsed_dates.isnull().sum()
            report["error"] = "Invalid date format"
            report["issues"].append(f"{invalid_count} records have unparseable joining dates.")
            return report
        # Standardise date strings to YYYY-MM-DD
        df_mapped['joining_date'] = parsed_dates.dt.strftime('%Y-%m-%d')
    else:
        # If joining date is missing, let's create a default today date
        df_mapped['joining_date'] = datetime.today().strftime('%Y-%m-%d')

    # 8. Run Profiling (from profile_data)
    profiling = profile_nulls_and_duplicates(df_mapped)
    quality_issues = identify_quality_issues(df_mapped)
    
    # 9. Handle Missing Values & Type Enforcement
    # Let's analyze missing value meanings
    missing_analysis = analyze_missing_values(df_mapped)
    
    # Run type enforcement (from type_enforcement)
    df_clean, type_report = enforce_types(df_mapped, auto_detect=True)

    # Convert numeric values for experience/salary safely if present
    if 'salary' in df_clean.columns:
        df_clean['salary'] = pd.to_numeric(df_clean['salary'], errors='coerce').fillna(0.0)
    if 'experience' in df_clean.columns:
        df_clean['experience'] = pd.to_numeric(df_clean['experience'], errors='coerce').fillna(0.0)

    # Boolean values mapping
    bool_cols = ['laptop_issued', 'access_granted', 'training_completed', 'email_setup', 'onboarding_complete']
    for col in bool_cols:
        if col in df_clean.columns:
            # map to boolean
            df_clean[col] = df_clean[col].astype(str).str.lower().str.strip().map({
                'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False, 'y': True, 'n': False,
                '1.0': True, '0.0': False, 'true.0': True, 'false.0': False
            }).fillna(False)
        else:
            # Missing fields default to False to reflect actual data state
            df_clean[col] = False

    # Fill basic missing strings
    string_cols = ['email', 'phone', 'department', 'designation', 'manager', 'onboarding_status', 'github_username', 'slack_id', 'jira_id', 'location', 'employment_type']
    for col in string_cols:
        if col in df_clean.columns:
            # Handle categorical columns by converting to object first
            if pd.api.types.is_categorical_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].astype('object')
            df_clean[col] = df_clean[col].fillna("Unknown")
        else:
            df_clean[col] = "Unknown"

    # Save to SQLite database
    db: Session = SessionLocal()
    try:
        logger.info(f"Starting database insertion for {len(df_clean)} employees")
        logger.info(f"DataFrame columns: {df_clean.columns.tolist()}")
        logger.info(f"DataFrame shape: {df_clean.shape}")
        
        # Clear existing records for this user only
        if user_id:
            cleared = db.query(Employee).filter(Employee.user_id == user_id).delete()
            logger.info(f"Cleared {cleared} existing employee records for user {user_id}")
        else:
            cleared = db.query(Employee).delete()
            logger.info(f"Cleared {cleared} all employee records (no user_id provided)")
        
        # Add all new active employees
        success_count = 0
        for idx, (_, row) in enumerate(df_clean.iterrows()):
            try:
                emp_obj = Employee(
                    user_id=user_id if user_id else 1,  # Default to user 1 if not provided
                    employee_id=str(row['employee_id']),
                    employee_name=str(row['employee_name']),
                    email=str(row['email']),
                    phone=str(row['phone']),
                    department=str(row['department']),
                    designation=str(row['designation']),
                    manager=str(row['manager']),
                    joining_date=str(row['joining_date']),
                    onboarding_status=str(row['onboarding_status']),
                    laptop_issued=bool(row['laptop_issued']),
                    access_granted=bool(row['access_granted']),
                    training_completed=bool(row['training_completed']) if 'training_completed' in row else False,
                    email_setup=bool(row['email_setup']) if 'email_setup' in row else False,
                    onboarding_complete=bool(row['onboarding_complete']) if 'onboarding_complete' in row else False,
                    github_username=str(row['github_username']),
                    slack_id=str(row['slack_id']),
                    jira_id=str(row['jira_id']),
                    location=str(row['location']),
                    employment_type=str(row['employment_type']),
                    salary=float(row['salary']) if 'salary' in row else 0.0,
                    experience=float(row['experience']) if 'experience' in row else 0.0,
                    slack_messages=int(row['slack_messages']) if 'slack_messages' in row else 0,
                    github_commits=int(row['github_commits']) if 'github_commits' in row else 0,
                    jira_tickets_resolved=int(row['jira_tickets_resolved']) if 'jira_tickets_resolved' in row else 0,
                    slack_reactions=int(row['slack_reactions']) if 'slack_reactions' in row else 0,
                    github_prs_reviewed=int(row['github_prs_reviewed']) if 'github_prs_reviewed' in row else 0,
                    laptop_issued_date=_optional_value(row, 'laptop_issued_date'),
                    email_setup_date=_optional_value(row, 'email_setup_date'),
                    access_granted_date=_optional_value(row, 'access_granted_date'),
                    training_completed_date=_optional_value(row, 'training_completed_date'),
                    onboarding_complete_date=_optional_value(row, 'onboarding_complete_date')
                )
                db.add(emp_obj)
                success_count += 1
                
                if (idx + 1) % 50 == 0:
                    logger.info(f"Processed {idx + 1}/{len(df_clean)} employees")
                    
            except Exception as emp_error:
                logger.error(f"Error inserting employee {row.get('employee_id', 'unknown')}: {str(emp_error)}")
                logger.error(f"Row data: {row.to_dict()}")
                raise
        
        db.commit()
        logger.info(f"Successfully committed {success_count} employees to database")
        
    except Exception as e:
        db.rollback()
        error_detail = f"Database error: {str(e)}"
        logger.error(error_detail)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(traceback.format_exc())
        report["error"] = error_detail
        report["issues"].append(error_detail)
        return report
    finally:
        db.close()

    # 10. Generate the standard processed datasets for OnboardIQ to ensure dashboard integration
    processed_dir = Path("data/processed")
    os.makedirs(processed_dir, exist_ok=True)

    # Write employees_processed.csv
    # Mapping columns to what standard employees table has: ID, Name, Department, Joining Date
    df_emp_out = df_clean[['employee_id', 'employee_name', 'department', 'joining_date']].copy()
    df_emp_out.columns = ['ID', 'Name', 'Department', 'Joining Date']
    df_emp_out.to_csv(processed_dir / "employees_processed.csv", index=False)

    # Write onboarding_processed.csv
    # Schema: Employee ID, Laptop Issued, Training Completed, Security Access Granted, Email Setup, Onboarding Complete
    df_onb_out = pd.DataFrame({
        'Employee ID': df_clean['employee_id'],
        'Laptop Issued': df_clean['laptop_issued'],
        'Training Completed': df_clean.get('training_completed', False),
        'Security Access Granted': df_clean['access_granted'],
        'Email Setup': df_clean.get('email_setup', False),
        'Onboarding Complete': df_clean.get('onboarding_complete', False)
    })
    df_onb_out.to_csv(processed_dir / "onboarding_processed.csv", index=False)

    # Write tools_processed.csv
    # Schema: Employee ID, Slack Messages, GitHub Commits, Jira Tickets Resolved, Slack Reactions, GitHub PRs Reviewed
    # Only use actual tool data from uploaded file, default to 0 if not provided
    df_tools_out = pd.DataFrame({
        'Employee ID': df_clean['employee_id'],
        'Slack Messages': df_clean.get('slack_messages', 0),
        'GitHub Commits': df_clean.get('github_commits', 0),
        'Jira Tickets Resolved': df_clean.get('jira_tickets_resolved', 0),
        'Slack Reactions': df_clean.get('slack_reactions', 0),
        'GitHub PRs Reviewed': df_clean.get('github_prs_reviewed', 0)
    })
    df_tools_out.to_csv(processed_dir / "tools_processed.csv", index=False)

    # Write support_processed.csv
    # Schema: Ticket ID, Employee ID, Issue Type, Resolution Time (hours), Status, Priority
    # Only create support data if actually provided in uploaded file
    support_cols = ['ticket_id', 'employee_id', 'issue_type', 'resolution_time_hours', 'status', 'priority']
    if all(col in df_clean.columns for col in support_cols):
        df_supp_out = df_clean[support_cols].copy()
        df_supp_out.columns = ['Ticket ID', 'Employee ID', 'Issue Type', 'Resolution Time (hours)', 'Status', 'Priority']
    else:
        # No support data provided - create empty file with correct schema
        df_supp_out = pd.DataFrame(columns=['Ticket ID', 'Employee ID', 'Issue Type', 'Resolution Time (hours)', 'Status', 'Priority'])
    df_supp_out.to_csv(processed_dir / "support_processed.csv", index=False)

    # Save summary report (preprocess_pipeline output simulation)
    # Output preprocessing_summary.json
    pipeline_summary = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_status": "SUCCESS",
        "datasets_processed": 4,
        "datasets_successful": 4,
        "datasets_failed": 0,
        "dataset_details": {
            "employees": {"status": "SUCCESS", "rows": len(df_clean), "columns": len(df_clean.columns)},
            "onboarding": {"status": "SUCCESS", "rows": len(df_onb_out), "columns": len(df_onb_out.columns)},
            "tools": {"status": "SUCCESS", "rows": len(df_tools_out), "columns": len(df_tools_out.columns)},
            "support": {"status": "SUCCESS", "rows": len(df_supp_out), "columns": len(df_supp_out.columns)}
        }
    }
    os.makedirs("output", exist_ok=True)
    with open("output/preprocessing_summary.json", "w") as f:
        json.dump(pipeline_summary, f, indent=2)

    # 11. Compile final stats
    end_time = datetime.now()
    processing_time_ms = int((end_time - start_time).total_seconds() * 1000)

    report["passed"] = True
    report["rows"] = len(df_clean)
    report["columns"] = len(df.columns)
    
    # Save active upload metadata
    save_upload_status({
        "status": "active",
        "active_file": os.path.basename(filepath),
        "rows": report["rows"],
        "columns": report["columns"],
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "validation_passed": True,
        "processing_time_ms": processing_time_ms
    }, user_id=user_id)

    return report

