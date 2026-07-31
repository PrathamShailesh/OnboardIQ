import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
import pandas as pd
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# Pydantic models for authentication requests
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

from app.database import engine, get_db, Base
from app.models import Employee, User
from app.upload_manager import (
    process_and_validate_upload, 
    get_upload_status, 
    restore_synthetic_data,
    init_upload_dir,
    get_user_upload_dir,
    get_user_metadata_file
)
from app.bottleneck_analyzer import BottleneckAnalyzer
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Ensure tables are created in SQLite
Base.metadata.create_all(bind=engine)


def migrate_employee_schema():
    """Add optional employee fields and user_id to existing local SQLite databases."""
    if engine.dialect.name != "sqlite":
        return

    timestamp_columns = (
        "laptop_issued_date",
        "email_setup_date",
        "access_granted_date",
        "training_completed_date",
        "onboarding_complete_date",
    )
    existing_columns = {column["name"] for column in inspect(engine).get_columns("employees")}

    with engine.begin() as connection:
        # Add user_id column if it doesn't exist
        if "user_id" not in existing_columns:
            connection.execute(text("ALTER TABLE employees ADD COLUMN user_id INTEGER"))
            connection.execute(text("ALTER TABLE employees ADD COLUMN FOREIGN KEY (user_id) REFERENCES users(id)"))
        
        # Add timestamp columns if they don't exist
        for column in timestamp_columns:
            if column not in existing_columns:
                connection.execute(text(f"ALTER TABLE employees ADD COLUMN {column} TEXT"))


migrate_employee_schema()

app = FastAPI(title="OnboardIQ Analytics API")

# Configure allowed browser origins through CORS_ORIGINS in production, for
# example: https://dashboard.example.com. Local origins remain the default.
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "OnboardIQ API is running",
        "timestamp": datetime.now().isoformat(),
        "upload_status": get_upload_status()  # Public endpoint, no user_id
    }

# Authentication endpoints
@app.post("/auth/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(request.password)
    new_user = User(
        email=request.email,
        username=request.username,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }

@app.post("/auth/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}

@app.get("/auth/me")
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "is_active": current_user.is_active
    }

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    # Use user-specific upload directory (temporarily using user_id=1 for debugging)
    user_upload_dir = get_user_upload_dir(1)
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Verify file extension
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.csv', '.xlsx']:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # 2. Save temporary upload file to user-specific directory
    temp_filepath = user_upload_dir / f"uploaded_raw{ext}"
    try:
        with open(temp_filepath, "wb") as buffer:
            shutil_copy = file.file
            # Read and write chunks
            while chunk := shutil_copy.read(1024 * 1024):
                buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # 3. Parse and run validation/preprocessing with user_id (temporarily using user_id=1 for debugging)
    report = process_and_validate_upload(str(temp_filepath), user_id=1)
    
    # Clean up temp file
    if os.path.exists(temp_filepath):
        try:
            os.remove(temp_filepath)
        except Exception:
            pass
            
    if not report["passed"]:
        # Raise 400 Bad Request with details
        raise HTTPException(status_code=400, detail={"message": report["error"], "issues": report.get("issues", [])})
        
    return {
        "status": "success",
        "filename": report["filename"],
        "rows": report["rows"],
        "columns": report["columns"]
    }

@app.get("/upload/status")
def upload_status(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    return get_upload_status(1)  # Temporarily using user_id=1

@app.delete("/upload")
def delete_upload(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    try:
        restore_synthetic_data(1)  # Temporarily using user_id=1
        return {"status": "success", "message": "Uploaded dataset removed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove uploaded data: {str(e)}")

@app.get("/employees")
def list_employees(
    db: Session = Depends(get_db), 
    page: int = 1, 
    limit: int = 10,
    search: Optional[str] = None
):  # Temporarily removed auth for debugging
    status = get_upload_status(1)  # Temporarily using user_id=1
    
    # 1. Load active data for current user (temporarily using user_id=1)
    if status["status"] == "active":
        # Read from SQLite database filtered by user_id
        query = db.query(Employee).filter(Employee.user_id == 1)
        if search:
            query = query.filter(
                Employee.employee_name.contains(search) | 
                Employee.department.contains(search) | 
                Employee.employee_id.contains(search)
            )
        total = query.count()
        employees = query.offset((page - 1) * limit).limit(limit).all()
        
        # Convert objects to dicts
        data = []
        for emp in employees:
            data.append({
                "employee_id": emp.employee_id,
                "employee_name": emp.employee_name,
                "email": emp.email,
                "phone": emp.phone,
                "department": emp.department,
                "designation": emp.designation,
                "manager": emp.manager,
                "joining_date": emp.joining_date,
                "onboarding_status": emp.onboarding_status,
                "laptop_issued": emp.laptop_issued,
                "access_granted": emp.access_granted,
                "github_username": emp.github_username,
                "slack_id": emp.slack_id,
                "jira_id": emp.jira_id,
                "location": emp.location,
                "employment_type": emp.employment_type,
                "salary": emp.salary,
                "experience": emp.experience
            })
    else:
        return {"total": 0, "page": page, "limit": limit, "data": []}

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }

@app.get("/employees/{employee_id}")
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    status = get_upload_status()
    if status["status"] == "active":
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {
            "employee_id": emp.employee_id,
            "employee_name": emp.employee_name,
            "email": emp.email,
            "phone": emp.phone,
            "department": emp.department,
            "designation": emp.designation,
            "manager": emp.manager,
            "joining_date": emp.joining_date,
            "onboarding_status": emp.onboarding_status,
            "laptop_issued": emp.laptop_issued,
            "access_granted": emp.access_granted,
            "github_username": emp.github_username,
            "slack_id": emp.slack_id,
            "jira_id": emp.jira_id,
            "location": emp.location,
            "employment_type": emp.employment_type,
            "salary": emp.salary,
            "experience": emp.experience
        }
    else:
        # Fallback lookup in CSV
        res = list_employees(db, page=1, limit=1000)
        for emp in res["data"]:
            if str(emp["employee_id"]) == str(employee_id):
                return emp
        raise HTTPException(status_code=404, detail="Employee not found")

@app.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    """Calculates all key metrics and statistics dynamically from active data for current user."""
    print("DEBUG: /dashboard/summary endpoint called")
    
    # Get upload status for user 1 (temporarily)
    status = get_upload_status(1)
    if status["status"] != "active":
        return {
            "active_onboardees": 0,
            "avg_onboarding_speed": "Not available from this dataset",
            "tool_adoption_rate": "Not available from this dataset",
            "open_tickets": 0,
            "cohorts": [],
            "onboarding_milestones": {"laptop": 0, "training": 0, "access": 0, "email": 0, "complete": 0, "total": 0},
            "stage_delays": {},
            "tool_engagement": {"slack_messages": 0, "github_commits": 0, "jira_resolved": 0},
            "ticket_categories": {},
            "total_employees": 0,
        }
    
    # Get employees for user 1 (temporarily)
    employees = db.query(Employee).filter(Employee.user_id == 1).all()
    
    if not employees:
        return {
            "active_onboardees": 0,
            "avg_onboarding_speed": "Not available from this dataset",
            "tool_adoption_rate": "Not available from this dataset",
            "open_tickets": 0,
            "cohorts": [],
            "onboarding_milestones": {"laptop": 0, "training": 0, "access": 0, "email": 0, "complete": 0, "total": 0},
            "stage_delays": {},
            "tool_engagement": {"slack_messages": 0, "github_commits": 0, "jira_resolved": 0},
            "ticket_categories": {},
            "total_employees": 0,
        }
    
    # Calculate metrics
    total_employees = len(employees)
    active_onboardees = sum(1 for emp in employees if not emp.onboarding_complete)
    
    # Calculate milestones
    laptop_count = sum(1 for emp in employees if emp.laptop_issued)
    access_count = sum(1 for emp in employees if emp.access_granted)
    training_count = sum(1 for emp in employees if emp.training_completed)
    email_count = sum(1 for emp in employees if emp.email_setup)
    complete_count = sum(1 for emp in employees if emp.onboarding_complete)
    
    # Calculate Average Onboarding Speed from actual date data
    avg_speed = "Not available from this dataset"
    completed_with_dates = [
        emp for emp in employees 
        if emp.onboarding_complete and emp.joining_date and emp.onboarding_complete_date
    ]
    if completed_with_dates:
        try:
            from datetime import datetime
            total_days = 0
            valid_count = 0
            for emp in completed_with_dates:
                try:
                    # Try parsing with time component first, then without
                    joining_str = str(emp.joining_date).split()[0]  # Take date part only
                    complete_str = str(emp.onboarding_complete_date).split()[0]  # Take date part only
                    joining = datetime.strptime(joining_str, '%Y-%m-%d')
                    complete = datetime.strptime(complete_str, '%Y-%m-%d')
                    if complete > joining:
                        total_days += (complete - joining).days
                        valid_count += 1
                except:
                    continue
            if valid_count > 0:
                avg_speed = f"{total_days / valid_count:.1f} days"
        except:
            pass
    
    # Calculate Tool Adoption Rate from actual tool usage
    tool_adoption = "Not available from this dataset"
    employees_with_tool_activity = sum(
        1 for emp in employees 
        if (emp.slack_messages or 0) > 0 or (emp.github_commits or 0) > 0 or (emp.jira_tickets_resolved or 0) > 0
    )
    if total_employees > 0:
        adoption_rate = (employees_with_tool_activity / total_employees) * 100
        if employees_with_tool_activity > 0:
            tool_adoption = f"{adoption_rate:.1f}%"
    
    # Calculate cohorts from department data
    cohorts = []
    dept_stats = {}
    for emp in employees:
        dept = emp.department if emp.department and emp.department != "Unknown" else "Unassigned"
        if dept not in dept_stats:
            dept_stats[dept] = {"total": 0, "complete": 0}
        dept_stats[dept]["total"] += 1
        if emp.onboarding_complete:
            dept_stats[dept]["complete"] += 1
    
    for dept, stats in dept_stats.items():
        if stats["total"] > 0:
            completion_rate = (stats["complete"] / stats["total"]) * 100
            cohorts.append({
                "name": dept,
                "code": dept[:3].upper(),
                "members": stats["total"],
                "completion_rate": round(completion_rate, 1)
            })
    
    # Calculate tool engagement from actual data
    total_slack = sum(emp.slack_messages or 0 for emp in employees)
    total_github = sum(emp.github_commits or 0 for emp in employees)
    total_jira = sum(emp.jira_tickets_resolved or 0 for emp in employees)
    
    # Calculate open tickets from support data (if available)
    open_tickets = 0
    ticket_categories = {}
    try:
        import pandas as pd
        from pathlib import Path
        support_file = Path("data/processed/support_processed.csv")
        if support_file.exists():
            df_support = pd.read_csv(support_file)
            if not df_support.empty and 'Status' in df_support.columns:
                open_tickets = len(df_support[df_support['Status'].isin(['Open', 'In Progress'])])
                if 'Issue Type' in df_support.columns:
                    open_by_type = df_support[df_support['Status'].isin(['Open', 'In Progress'])]
                    for issue_type in open_by_type['Issue Type'].unique():
                        ticket_categories[issue_type] = len(open_by_type[open_by_type['Issue Type'] == issue_type])
    except:
        pass
    
    return {
        "active_onboardees": active_onboardees,
        "avg_onboarding_speed": avg_speed,
        "tool_adoption_rate": tool_adoption,
        "open_tickets": open_tickets,
        "cohorts": cohorts,
        "onboarding_milestones": {
            "laptop": laptop_count,
            "training": training_count,
            "access": access_count,
            "email": email_count,
            "complete": complete_count,
            "total": total_employees
        },
        "stage_delays": {},
        "tool_engagement": {
            "slack_messages": total_slack,
            "github_commits": total_github,
            "jira_resolved": total_jira
        },
        "ticket_categories": ticket_categories,
        "total_employees": total_employees,
    }

@app.get("/onboarding/details")
def get_onboarding_details(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    """Returns detailed onboarding progress data for current user's employees."""
    if get_upload_status(1)["status"] != "active":  # Temporarily using user_id=1
        return {"data": []}

    employees = db.query(Employee).filter(Employee.user_id == 1).all()  # Temporarily using user_id=1
    
    if not employees:
        return {"data": []}
    
    data = []
    for emp in employees:
        data.append({
            "employee_id": emp.employee_id,
            "employee_name": emp.employee_name,
            "department": emp.department,
            "joining_date": emp.joining_date,
            "laptop_issued": bool(emp.laptop_issued),
            "training_completed": bool(emp.training_completed),
            "access_granted": bool(emp.access_granted),
            "email_setup": bool(emp.email_setup),
            "onboarding_complete": bool(emp.onboarding_complete)
        })
    
    return {"data": data}

@app.get("/tools/details")
def get_tools_details(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    """Returns detailed tool engagement data for current user's employees."""
    if get_upload_status(1)["status"] != "active":  # Temporarily using user_id=1
        return {"data": []}

    employees = db.query(Employee).filter(Employee.user_id == 1).all()  # Temporarily using user_id=1
    
    if not employees:
        return {"data": []}
    
    # Use actual tool engagement data from Employee model
    data = []
    for emp in employees:
        data.append({
            "employee_id": emp.employee_id,
            "employee_name": emp.employee_name,
            "department": emp.department,
            "slack_messages": emp.slack_messages or 0,
            "github_commits": emp.github_commits or 0,
            "jira_tickets_resolved": emp.jira_tickets_resolved or 0,
            "slack_reactions": emp.slack_reactions or 0,
            "github_prs_reviewed": emp.github_prs_reviewed or 0
        })
    
    return {"data": data}

@app.get("/support/details")
def get_support_details():  # Temporarily removed auth for debugging
    """Returns detailed support ticket data for current user."""
    if get_upload_status(1)["status"] != "active":  # Temporarily using user_id=1
        return {"data": []}

    # Read support data from processed file if available
    try:
        import pandas as pd
        from pathlib import Path
        support_file = Path("data/processed/support_processed.csv")
        if support_file.exists():
            df_support = pd.read_csv(support_file)
            if not df_support.empty:
                # Map CSV columns to API response format
                data = []
                for _, row in df_support.iterrows():
                    data.append({
                        "ticket_id": row.get('Ticket ID', ''),
                        "employee_id": row.get('Employee ID', ''),
                        "employee_name": '',  # Would need to join with employee data
                        "issue_type": row.get('Issue Type', ''),
                        "resolution_time_hours": row.get('Resolution Time (hours)', None),
                        "status": row.get('Status', ''),
                        "priority": row.get('Priority', '')
                    })
                return {"data": data}
    except Exception as e:
        print(f"Error reading support data: {e}")
    
    return {"data": []}

@app.get('/bottlenecks/analysis')
def get_bottleneck_analysis(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    '''Returns comprehensive bottleneck analysis including rankings, delays, and risk predictions.'''
    if get_upload_status(1)["status"] != "active":  # Temporarily using user_id=1
        return {
            "bottlenecks": [],
            "department_delays": {},
            "risk_employees": [],
            "root_causes": {"total_delayed_employees": 0, "delay_reasons": {}, "ticket_impact": {}},
            "summary": {"total_employees": 0, "total_bottlenecks": 0, "top_bottleneck": None, "at_risk_count": 0},
        }

    # Get current user's employees from database (temporarily using user_id=1)
    employees = db.query(Employee).filter(Employee.user_id == 1).all()
    
    if not employees:
        return {
            "bottlenecks": [],
            "department_delays": {},
            "risk_employees": [],
            "root_causes": {"total_delayed_employees": 0, "delay_reasons": {}, "ticket_impact": {}},
            "summary": {"total_employees": 0, "total_bottlenecks": 0, "top_bottleneck": None, "at_risk_count": 0},
        }
    
    # Convert to DataFrame for bottleneck analyzer
    df_emp = pd.DataFrame([{
        'ID': emp.employee_id,
        'Name': emp.employee_name,
        'Department': emp.department,
        'Joining Date': emp.joining_date,
        'Laptop Issued': bool(emp.laptop_issued),
        'Security Access Granted': bool(emp.access_granted),
        'Onboarding Complete': bool(emp.onboarding_complete),
        'Training Completed': bool(emp.training_completed),
        'Email Setup': bool(emp.email_setup)
    } for emp in employees])
    
    # Create onboarding data from employee records
    df_onb = pd.DataFrame([{
        'Employee ID': emp.employee_id,
        'Laptop Issued': bool(emp.laptop_issued),
        'Training Completed': bool(emp.training_completed),
        'Security Access Granted': bool(emp.access_granted),
        'Email Setup': bool(emp.email_setup),
        'Onboarding Complete': bool(emp.onboarding_complete)
    } for emp in employees])
    
    # Create temporary CSV files for bottleneck analyzer
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_emp.to_csv(f.name, index=False)
        temp_emp_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_onb.to_csv(f.name, index=False)
        temp_onb_path = f.name
    
    # Load support data if available
    temp_supp_path = None
    try:
        from pathlib import Path
        support_file = Path("data/processed/support_processed.csv")
        if support_file.exists():
            temp_supp_path = str(support_file)
    except:
        pass
    
    try:
        analyzer = BottleneckAnalyzer(temp_emp_path, temp_onb_path, temp_supp_path)
        report = analyzer.generate_bottleneck_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to generate bottleneck analysis: {str(e)}')
    finally:
        # Clean up temporary files
        import os
        for path in [temp_emp_path, temp_onb_path]:
            if path and os.path.exists(path):
                os.remove(path)


@app.get('/bottlenecks/ranking')
def get_bottleneck_ranking(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    '''Returns ranked list of bottlenecks by severity for current user.'''
    if get_upload_status(1)["status"] != "active":  # Temporarily using user_id=1
        return {'bottlenecks': []}

    employees = db.query(Employee).filter(Employee.user_id == 1).all()  # Temporarily using user_id=1
    
    if not employees:
        return {'bottlenecks': []}
    
    # Convert to DataFrame for bottleneck analyzer
    df_emp = pd.DataFrame([{
        'ID': emp.employee_id,
        'Name': emp.employee_name,
        'Department': emp.department,
        'Joining Date': emp.joining_date,
        'Laptop Issued': bool(emp.laptop_issued),
        'Security Access Granted': bool(emp.access_granted),
        'Onboarding Complete': bool(emp.onboarding_complete),
        'Training Completed': bool(emp.training_completed),
        'Email Setup': bool(emp.email_setup)
    } for emp in employees])
    
    # Create onboarding data from employee records
    df_onb = pd.DataFrame([{
        'Employee ID': emp.employee_id,
        'Laptop Issued': bool(emp.laptop_issued),
        'Training Completed': bool(emp.training_completed),
        'Security Access Granted': bool(emp.access_granted),
        'Email Setup': bool(emp.email_setup),
        'Onboarding Complete': bool(emp.onboarding_complete)
    } for emp in employees])
    
    # Create temporary CSV files for bottleneck analyzer
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_emp.to_csv(f.name, index=False)
        temp_emp_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_onb.to_csv(f.name, index=False)
        temp_onb_path = f.name
    
    try:
        analyzer = BottleneckAnalyzer(temp_emp_path, temp_onb_path)
        df, _ = analyzer.load_data()
        delays = analyzer.calculate_stage_delays(df)
        ranked = analyzer.rank_bottlenecks(delays)
        return {'bottlenecks': ranked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to generate bottleneck ranking: {str(e)}')
    finally:
        # Clean up temporary files
        import os
        for path in [temp_emp_path, temp_onb_path]:
            if path and os.path.exists(path):
                os.remove(path)


@app.get('/bottlenecks/department-delays')
def get_department_delays(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    '''Returns average onboarding delays by department for current user.'''
    if get_upload_status(1)["status"] != "active":  # Temporarily using user_id=1
        return {'department_delays': {}}

    employees = db.query(Employee).filter(Employee.user_id == 1).all()  # Temporarily using user_id=1
    
    if not employees:
        return {'department_delays': {}}
    
    # Convert to DataFrame for bottleneck analyzer
    df_emp = pd.DataFrame([{
        'ID': emp.employee_id,
        'Name': emp.employee_name,
        'Department': emp.department,
        'Joining Date': emp.joining_date,
        'Laptop Issued': bool(emp.laptop_issued),
        'Security Access Granted': bool(emp.access_granted),
        'Onboarding Complete': bool(emp.onboarding_complete),
        'Training Completed': bool(emp.training_completed),
        'Email Setup': bool(emp.email_setup)
    } for emp in employees])
    
    # Create onboarding data from employee records
    df_onb = pd.DataFrame([{
        'Employee ID': emp.employee_id,
        'Laptop Issued': bool(emp.laptop_issued),
        'Training Completed': bool(emp.training_completed),
        'Security Access Granted': bool(emp.access_granted),
        'Email Setup': bool(emp.email_setup),
        'Onboarding Complete': bool(emp.onboarding_complete)
    } for emp in employees])
    
    # Create temporary CSV files for bottleneck analyzer
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_emp.to_csv(f.name, index=False)
        temp_emp_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_onb.to_csv(f.name, index=False)
        temp_onb_path = f.name
    
    try:
        analyzer = BottleneckAnalyzer(temp_emp_path, temp_onb_path)
        df, _ = analyzer.load_data()
        delays = analyzer.calculate_department_delays(df)
        return {'department_delays': delays}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to generate department delays: {str(e)}')
    finally:
        # Clean up temporary files
        import os
        for path in [temp_emp_path, temp_onb_path]:
            if path and os.path.exists(path):
                os.remove(path)


@app.get('/bottlenecks/risk-employees')
def get_risk_employees(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    '''Returns employees at risk of exceeding 30-day onboarding for current user.'''
    if get_upload_status(1)["status"] != "active":  # Temporarily using user_id=1
        return {'risk_employees': []}

    employees = db.query(Employee).filter(Employee.user_id == 1).all()  # Temporarily using user_id=1
    
    if not employees:
        return {'risk_employees': []}
    
    # Convert to DataFrame for bottleneck analyzer
    df_emp = pd.DataFrame([{
        'ID': emp.employee_id,
        'Name': emp.employee_name,
        'Department': emp.department,
        'Joining Date': emp.joining_date,
        'Laptop Issued': bool(emp.laptop_issued),
        'Security Access Granted': bool(emp.access_granted),
        'Onboarding Complete': bool(emp.onboarding_complete),
        'Training Completed': bool(emp.training_completed),
        'Email Setup': bool(emp.email_setup)
    } for emp in employees])
    
    # Create onboarding data from employee records
    df_onb = pd.DataFrame([{
        'Employee ID': emp.employee_id,
        'Laptop Issued': bool(emp.laptop_issued),
        'Training Completed': bool(emp.training_completed),
        'Security Access Granted': bool(emp.access_granted),
        'Email Setup': bool(emp.email_setup),
        'Onboarding Complete': bool(emp.onboarding_complete)
    } for emp in employees])
    
    # Create temporary CSV files for bottleneck analyzer
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_emp.to_csv(f.name, index=False)
        temp_emp_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_onb.to_csv(f.name, index=False)
        temp_onb_path = f.name
    
    try:
        analyzer = BottleneckAnalyzer(temp_emp_path, temp_onb_path)
        df, _ = analyzer.load_data()
        risk_employees = analyzer.identify_risk_employees(df)
        return {'risk_employees': risk_employees}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to identify risk employees: {str(e)}')
    finally:
        # Clean up temporary files
        import os
        for path in [temp_emp_path, temp_onb_path]:
            if path and os.path.exists(path):
                os.remove(path)


@app.get('/bottlenecks/root-causes')
def get_root_causes(db: Session = Depends(get_db)):  # Temporarily removed auth for debugging
    '''Returns analysis of root causes for delays for current user.'''
    if get_upload_status(1)["status"] != "active":  # Temporarily using user_id=1
        return {"total_delayed_employees": 0, "delay_reasons": {}, "ticket_impact": {}}

    employees = db.query(Employee).filter(Employee.user_id == 1).all()  # Temporarily using user_id=1
    
    if not employees:
        return {"total_delayed_employees": 0, "delay_reasons": {}, "ticket_impact": {}}
    
    # Convert to DataFrame for bottleneck analyzer
    df_emp = pd.DataFrame([{
        'ID': emp.employee_id,
        'Name': emp.employee_name,
        'Department': emp.department,
        'Joining Date': emp.joining_date,
        'Laptop Issued': bool(emp.laptop_issued),
        'Security Access Granted': bool(emp.access_granted),
        'Onboarding Complete': bool(emp.onboarding_complete),
        'Training Completed': bool(emp.training_completed),
        'Email Setup': bool(emp.email_setup)
    } for emp in employees])
    
    # Create onboarding data from employee records
    df_onb = pd.DataFrame([{
        'Employee ID': emp.employee_id,
        'Laptop Issued': bool(emp.laptop_issued),
        'Training Completed': bool(emp.training_completed),
        'Security Access Granted': bool(emp.access_granted),
        'Email Setup': bool(emp.email_setup),
        'Onboarding Complete': bool(emp.onboarding_complete)
    } for emp in employees])
    
    # Create temporary CSV files for bottleneck analyzer
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_emp.to_csv(f.name, index=False)
        temp_emp_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df_onb.to_csv(f.name, index=False)
        temp_onb_path = f.name
    
    # Load support data if available
    temp_supp_path = None
    try:
        from pathlib import Path
        support_file = Path("data/processed/support_processed.csv")
        if support_file.exists():
            temp_supp_path = str(support_file)
    except:
        pass
    
    try:
        analyzer = BottleneckAnalyzer(temp_emp_path, temp_onb_path, temp_supp_path)
        df, df_supp = analyzer.load_data()
        root_causes = analyzer.analyze_root_causes(df, df_supp)
        return root_causes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to analyze root causes: {str(e)}')
    finally:
        # Clean up temporary files
        import os
        for path in [temp_emp_path, temp_onb_path]:
            if path and os.path.exists(path):
                os.remove(path)






