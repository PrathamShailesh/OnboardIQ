This `README.md` is designed to be the professional front door for your repository. It communicates what the project is, how to set it up, and how your team is collaborating.

Create a file named `README.md` in the root of your project directory and paste this content:

---

# OnboardIQ

**Transforming Employee Onboarding Data into Actionable Productivity Insights.**

## 1. Project Overview

OnboardIQ is a prototype analytics platform designed to help organizations identify operational bottlenecks during the first 30 days of employee onboarding. By unifying onboarding progress, internal tool usage, and IT support ticket history, leadership can make data-driven decisions to improve employee productivity.

## 2. Team Members

* **Pratham Shailesh Dsouza:** Data Integration, Cleaning, and KPI Development
* **Samarth S Alva:** Backend API Development and Database Design
* **Vivan Raj Mittakodi:** Frontend Dashboard UI and Data Visualization

## 3. Technology Stack

* **Frontend:** React.js
* **Backend:** FastAPI (Python)
* **Data Processing:** Pandas, NumPy
* **Data Generation:** Faker
* **Database:** SQLite/PostgreSQL
* **Visualization:** Plotly/Chart.js

## 4. Setup Instructions

### Prerequisites

* Python 3.10+
* Node.js (v18+)
* Git

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/PrathamShailesh/OnboardIQ.git
cd OnboardIQ

```


2. **Backend Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload

```


3. **Frontend Setup:**
```bash
cd frontend
npm install

# Run the dashboard
npm start

```



## 5. Engineering Workflow (Standardized)

This project follows strict engineering guidelines:

* **Branching:** All work must be done in feature branches (`feat/`, `fix/`, `chore/`).
* **Pull Requests:** No direct pushes to `main`. All code must pass peer review and be merged via PR.
* **Daily Standup:** Team sync happens at the start of every session.
* **Journaling:** Individual daily journals are submitted at the end of every session.

## 6. Data Architecture

* `data/generate_data.py`: Script to generate synthetic onboarding datasets.
* `data/*.csv`: Raw synthetic data files.
* `app/`: FastAPI backend implementation.
* `frontend/`: React dashboard application.

## 7. Upload data quality pipeline

Uploads accept CSV and XLSX employee data. `employee_id`, `employee_name`, and a valid
`joining_date` are required for a record to become active. Common headers such as `Employee ID`,
`Employee Name`, and `Joining Date` are mapped automatically. Optional fields include `email`,
`department`, `designation`, `location`, `employment_type`, `onboarding_status`,
`laptop_issued`, `training_completed`, `access_granted`, `email_setup`, `onboarding_complete`,
and real onboarding completion-date fields.

Text is trimmed, internal whitespace is collapsed, names are title-cased, emails lower-cased, and
known department aliases (for example `eng` and `hr`) are canonicalized. Dates are parsed safely
and emitted as `YYYY-MM-DD`; invalid dates are reported, never replaced with invented dates.
Exact duplicates and repeated employee IDs are removed deterministically (the first valid record
is retained). Invalid records are not loaded into the active employee database.

Every upload writes these auditable files under `output/`:

* `data_quality_report.json` — processing, normalization, conversion, validation, merge, and feature summaries.
* `removed_duplicates.csv` — every removed duplicate and its reason.
* `validation_failures.csv` — rejected records with `validation_reasons`.
* `unmatched_<source>_records.csv` and `employees_without_<source>.csv` — produced when optional related sources are merge-validated.

Dashboard KPIs use only supplied valid data. Metrics without supporting source columns or real
completion dates are returned as `unavailable` rather than synthetic estimates.

## 8. Employee Dataset Upload

OnboardIQ supports uploading real employee datasets to replace synthetic demo data.

### Supported File Formats
- **CSV** (.csv)
- **Excel** (.xlsx)

### Upload Process
1. Navigate to the **Employee Upload** tab in the dashboard
2. Drag & drop your employee dataset file or click **Browse File**
3. Click **Ingest Dataset** to upload
4. The system automatically validates and processes the file

### Validation
The upload system validates:
- File type (CSV/XLSX only)
- Required columns (employee_id, employee_name)
- Duplicate employee IDs
- Date format (joining_date)
- Missing values
- File corruption

### Pipeline Execution
After successful upload, the system automatically:
- Runs data profiling
- Handles missing values
- Enforces data types
- Generates processed datasets for all dashboard tabs
- Updates SQLite database with employee records

### Dashboard Integration
Once uploaded, the employee dataset is used across:
- **Overview Tab**: Active onboardees, cohorts, milestones
- **Onboarding Progress Tab**: Laptop, training, access, email completion
- **Tool Insights Tab**: GitHub, Slack, Jira engagement metrics
- **Support Tickets Tab**: IT support ticket analytics

If no upload exists, the dashboard continues using synthetic demo data.

### API Endpoints
- `POST /upload` - Upload employee dataset
- `GET /upload/status` - Get current upload status
- `DELETE /upload` - Delete upload and restore synthetic data
- `GET /employees` - List all employees (with pagination & search)
- `GET /employees/{employee_id}` - Get specific employee details
