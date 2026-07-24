import os
import shutil
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Employee

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

def init_upload_dir():
    """Ensure upload directory exists."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_upload_status() -> dict:
    """Returns the current upload status from metadata.json."""
    init_upload_dir()
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, "r") as f:
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

def save_upload_status(status_dict: dict):
    """Saves the upload status to metadata.json."""
    init_upload_dir()
    with open(METADATA_FILE, "w") as f:
        json.dump(status_dict, f, indent=2)

def clean_processed_dir():
    """Backup processed files if they are the original synthetic ones."""
    # We don't need active backup because we can restore by regenerating synthetic data
    pass

def restore_synthetic_data():
    """Restores synthetic datasets using the data generation script."""
    import subprocess
    cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 1. Regenerate raw data
    subprocess.run([sys.executable, "data/generate_data.py"], cwd=cwd, check=True)
    
    # 2. Run preprocess pipeline
    subprocess.run([sys.executable, "scripts/preprocess_pipeline.py"], cwd=cwd, check=True)

    # 3. Clear database table
    db = SessionLocal()
    try:
        db.query(Employee).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error clearing employee DB: {e}")
    finally:
        db.close()

    # 4. Save metadata status
    save_upload_status({
        "status": "idle",
        "active_file": None,
        "rows": 0,
        "columns": 0,
        "upload_time": None,
        "validation_passed": False,
        "processing_time_ms": 0
    })

def _legacy_process_and_validate_upload(filepath: str) -> dict:
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
        elif norm in ['github_username', 'github username']:
            column_mapping[col] = 'github_username'
        elif norm in ['slack_id', 'slack id']:
            column_mapping[col] = 'slack_id'
        elif norm in ['jira_id', 'jira id']:
            column_mapping[col] = 'jira_id'
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
            # Generate default values dynamically so that tabs have complete fields
            if col == 'laptop_issued':
                df_clean[col] = True
            elif col == 'access_granted':
                df_clean[col] = True
            elif col == 'training_completed':
                df_clean[col] = True
            elif col == 'email_setup':
                df_clean[col] = True
            elif col == 'onboarding_complete':
                df_clean[col] = True

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
        # Clear existing records
        db.query(Employee).delete()
        
        # Add all new active employees
        for _, row in df_clean.iterrows():
            emp_obj = Employee(
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
                github_username=str(row['github_username']),
                slack_id=str(row['slack_id']),
                jira_id=str(row['jira_id']),
                location=str(row['location']),
                employment_type=str(row['employment_type']),
                salary=float(row['salary']) if 'salary' in row else 0.0,
                experience=float(row['experience']) if 'experience' in row else 0.0
            )
            db.add(emp_obj)
        db.commit()
    except Exception as e:
        db.rollback()
        report["error"] = "Database error"
        report["issues"].append(f"Failed to write to database: {str(e)}")
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
        'Training Completed': df_clean.get('training_completed', True),
        'Security Access Granted': df_clean['access_granted'],
        'Email Setup': df_clean.get('email_setup', True),
        'Onboarding Complete': df_clean.get('onboarding_complete', True)
    })
    df_onb_out.to_csv(processed_dir / "onboarding_processed.csv", index=False)

    # Write tools_processed.csv
    # Schema: Employee ID, Slack Messages, GitHub Commits, Jira Tickets Resolved, Slack Reactions, GitHub PRs Reviewed
    # If the sheet doesn't contain tool fields, generate deterministic mock tools usage
    np.random.seed(42)
    df_tools_out = pd.DataFrame({
        'Employee ID': df_clean['employee_id'],
        'Slack Messages': df_clean.get('slack_messages', [np.random.randint(50, 450) for _ in range(len(df_clean))]),
        'GitHub Commits': df_clean.get('github_commits', [np.random.randint(5, 95) for _ in range(len(df_clean))]),
        'Jira Tickets Resolved': df_clean.get('jira_tickets_resolved', [np.random.randint(0, 45) for _ in range(len(df_clean))]),
        'Slack Reactions': df_clean.get('slack_reactions', [np.random.randint(10, 190) for _ in range(len(df_clean))]),
        'GitHub PRs Reviewed': df_clean.get('github_prs_reviewed', [np.random.randint(0, 25) for _ in range(len(df_clean))])
    })
    df_tools_out.to_csv(processed_dir / "tools_processed.csv", index=False)

    # Write support_processed.csv
    # Schema: Ticket ID, Employee ID, Issue Type, Resolution Time (hours), Status, Priority
    support_tickets = []
    # Create tickets for a portion of active onboardees
    for idx, emp_id in enumerate(df_clean['employee_id']):
        if idx % 3 == 0: # 33% of new hires get IT tickets
            support_tickets.append({
                'Ticket ID': f'TKT-{1000 + idx:04d}',
                'Employee ID': emp_id,
                'Issue Type': np.random.choice(['Hardware', 'Software', 'Network', 'Access', 'Account']),
                'Resolution Time (hours)': np.random.randint(1, 48),
                'Status': np.random.choice(['Open', 'In Progress', 'Resolved', 'Closed']),
                'Priority': np.random.choice(['Low', 'Medium', 'High', 'Critical'])
            })
    if not support_tickets:
        support_tickets.append({
            'Ticket ID': 'TKT-9999',
            'Employee ID': df_clean['employee_id'].iloc[0],
            'Issue Type': 'Hardware',
            'Resolution Time (hours)': 24,
            'Status': 'Resolved',
            'Priority': 'Medium'
        })
    df_supp_out = pd.DataFrame(support_tickets)
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
    })

    return report


def _db_value(row: pd.Series, column: str, default=None):
    """Return a database-safe scalar without hiding missing source data."""
    value = row.get(column, default)
    return default if pd.isna(value) else value


def process_and_validate_upload(filepath: str) -> dict:
    """Process a CSV/XLSX upload through the auditable onboarding quality pipeline."""
    started = datetime.now()
    report = {"passed": False, "error": None, "rows": 0, "columns": 0,
              "filename": os.path.basename(filepath), "issues": []}
    existence = validate_file_exists(filepath)
    if not existence["passed"]:
        report["error"] = existence["message"]
        return report
    fmt = validate_file_format(filepath, allowed_formats=["csv", "xlsx"])
    if not fmt["passed"]:
        report["error"] = "Unsupported file type"
        report["issues"].append(fmt["message"])
        return report
    try:
        if fmt["detected_format"] == "csv":
            source = pd.read_csv(filepath, encoding=detect_encoding(filepath).get("encoding", "utf-8"))
        else:
            source = pd.read_excel(filepath)
    except Exception:
        report["error"] = "Corrupted file"
        report["issues"].append("The uploaded file could not be read as a tabular dataset.")
        return report
    if source.empty:
        report["error"] = "Corrupted file"
        report["issues"].append("The uploaded dataset contains zero rows.")
        return report
    cleaned, quality = process_employee_dataframe(source)
    required = {"employee_id", "employee_name"}
    if not required.issubset(cleaned.columns):
        report["error"] = "Missing required columns"
        report["issues"].append("The dataset must contain employee_id and employee_name.")
        quality["warnings"].append(report["issues"][-1])
        save_quality_report(quality)
        return report
    valid = cleaned.loc[cleaned["passes_all_checks"]].copy()
    if valid.empty:
        report["error"] = "No valid employee records"
        report["issues"].append("All rows failed validation; see output/validation_failures.csv for reasons.")
        save_quality_report(quality)
        return report
    quality["kpis"] = calculate_kpis(valid)
    save_quality_report(quality)
    db: Session = SessionLocal()
    try:
        db.query(Employee).delete()
        for _, row in valid.iterrows():
            db.add(Employee(
                employee_id=str(_db_value(row, "employee_id", "")), employee_name=str(_db_value(row, "employee_name", "")),
                email=_db_value(row, "email"), phone=_db_value(row, "phone"), department=_db_value(row, "department"),
                designation=_db_value(row, "designation"), manager=_db_value(row, "manager"), joining_date=_db_value(row, "joining_date"),
                onboarding_status=_db_value(row, "onboarding_status"), laptop_issued=_db_value(row, "laptop_issued"),
                access_granted=_db_value(row, "access_granted"), github_username=_db_value(row, "github_username"),
                slack_id=_db_value(row, "slack_id"), jira_id=_db_value(row, "jira_id"), location=_db_value(row, "location"),
                employment_type=_db_value(row, "employment_type"), salary=_db_value(row, "salary"), experience=_db_value(row, "experience")))
        db.commit()
    except Exception as exc:
        db.rollback()
        report["error"] = "Database error"
        report["issues"].append(f"Failed to persist valid records: {exc}")
        return report
    finally:
        db.close()
    processed = Path("data/processed")
    processed.mkdir(parents=True, exist_ok=True)
    valid[["employee_id", "employee_name"] + [c for c in ("department", "joining_date") if c in valid]].rename(columns={"employee_id": "ID", "employee_name": "Name", "department": "Department", "joining_date": "Joining Date"}).to_csv(processed / "employees_processed.csv", index=False)
    onboarding_columns = [c for c in ["employee_id", "laptop_issued", "training_completed", "access_granted", "email_setup", "onboarding_complete"] if c in valid]
    if onboarding_columns:
        valid[onboarding_columns].rename(columns={"employee_id": "Employee ID", "laptop_issued": "Laptop Issued", "training_completed": "Training Completed", "access_granted": "Security Access Granted", "email_setup": "Email Setup", "onboarding_complete": "Onboarding Complete"}).to_csv(processed / "onboarding_processed.csv", index=False)
    # Do not manufacture tool use or tickets. Remove stale upload artifacts when absent.
    for stale in (processed / "tools_processed.csv", processed / "support_processed.csv"):
        if stale.exists(): stale.unlink()
    elapsed = int((datetime.now() - started).total_seconds() * 1000)
    report.update({"passed": True, "rows": len(valid), "columns": len(source) and len(source.columns), "quality_report": quality})
    save_upload_status({"status": "active", "active_file": report["filename"], "rows": len(valid), "columns": len(source.columns), "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "validation_passed": True, "processing_time_ms": elapsed, "quality_report": "output/data_quality_report.json"})
    return report
