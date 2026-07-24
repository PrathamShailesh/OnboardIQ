"""Auditable cleaning, validation, merging, and KPI helpers for onboarding data."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

OUTPUT_DIR = Path("output")
BOOLEAN_COLUMNS = {"laptop_issued", "access_granted", "training_completed", "email_setup", "onboarding_complete"}
MILESTONE_COLUMNS = ["laptop_issued", "training_completed", "access_granted", "email_setup"]
STATUS_VALUES = {"pending", "in_progress", "completed", "blocked"}
DEPARTMENT_ALIASES = {
    "eng": "Engineering", "engineering team": "Engineering", "engineering": "Engineering",
    "hr": "Human Resources", "human resources": "Human Resources",
    "it": "Information Technology", "information technology": "Information Technology",
}
CANONICAL_COLUMNS = {
    "id": "employee_id", "employee id": "employee_id", "employee_id": "employee_id",
    "name": "employee_name", "employee name": "employee_name", "employee_name": "employee_name",
    "joining date": "joining_date", "joining_date": "joining_date",
    "laptop issued": "laptop_issued", "security access granted": "access_granted",
    "access granted": "access_granted", "training completed": "training_completed",
    "email setup": "email_setup", "onboarding complete": "onboarding_complete",
    "onboarding status": "onboarding_status", "employment type": "employment_type",
}
TRUE_VALUES = {"true", "yes", "y", "1", "t"}
FALSE_VALUES = {"false", "no", "n", "0", "f"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def clean_text(value: Any) -> Any:
    """Trim and collapse whitespace without turning a missing value into text."""
    if pd.isna(value):
        return pd.NA
    return re.sub(r"\s+", " ", str(value).strip())


def normalize_column_name(name: Any) -> str:
    """Map common HR headers to the internal snake_case schema."""
    cleaned = clean_text(name).lower().replace("_", " ")
    return CANONICAL_COLUMNS.get(cleaned, cleaned.replace(" ", "_"))


def normalize_text_columns(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Normalize onboarding text fields and report values changed per column."""
    df = frame.copy()
    changes: dict[str, int] = {}
    for col in df.select_dtypes(include=["object", "string"]).columns:
        before = df[col].copy()
        df[col] = df[col].map(clean_text)
        if col == "employee_name":
            df[col] = df[col].str.title()
        elif col == "email":
            df[col] = df[col].str.lower()
        elif col == "department":
            df[col] = df[col].str.lower().map(DEPARTMENT_ALIASES).fillna(df[col].str.title())
        elif col in {"designation", "location", "employment_type"}:
            df[col] = df[col].str.title()
        elif col == "onboarding_status":
            status = df[col].str.lower().str.replace(" ", "_", regex=False)
            df[col] = status.replace({"inprogress": "in_progress", "complete": "completed"})
        changes[col] = int((before.fillna("").astype(str) != df[col].fillna("").astype(str)).sum())
    return df, changes


def parse_boolean(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return nullable booleans and an invalid-value mask for a supplied field."""
    text = series.map(clean_text).str.lower()
    parsed = text.map({**{v: True for v in TRUE_VALUES}, **{v: False for v in FALSE_VALUES}})
    invalid = text.notna() & parsed.isna()
    return parsed.astype("boolean"), invalid


def _parse_dates(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    parsed = df.copy()
    failures: dict[str, int] = {}
    date_columns = [c for c in parsed if c == "joining_date" or c.endswith("_date") or c.endswith("_completed_at")]
    for col in date_columns:
        original = parsed[col]
        values = pd.to_datetime(original, errors="coerce")
        failures[col] = int(original.notna().sum() - values.notna().sum())
        parsed[col] = values.dt.normalize()
    return parsed, failures


def _deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    source_ids = df.get("employee_id", pd.Series(dtype="string")).astype("string")
    source_duplicate_count = int(source_ids[source_ids.notna() & source_ids.duplicated(keep=False)].nunique())
    exact = df.duplicated(keep="first")
    removed = df.loc[exact].copy()
    removed["removal_reason"] = "exact_duplicate"
    retained = df.loc[~exact].copy()
    if "employee_id" not in retained:
        return retained, removed, {"exact_duplicates_removed": int(exact.sum()), "duplicate_employee_ids_detected": 0}
    ids = retained["employee_id"].astype("string")
    # Stable sort puts valid rows first, preserving source order among valid rows.
    valid = ids.notna() & ids.str.strip().ne("") & retained.get("employee_name", pd.Series(pd.NA, index=retained.index)).notna()
    ranked = retained.assign(_valid=valid, _source_order=range(len(retained))).sort_values(["employee_id", "_valid", "_source_order"], ascending=[True, False, True], na_position="last")
    keep_indices = ranked.drop_duplicates("employee_id", keep="first").index
    id_removed = retained.loc[~retained.index.isin(keep_indices) & ids.notna()].copy()
    id_removed["removal_reason"] = "duplicate_employee_id"
    retained = retained.loc[retained.index.isin(keep_indices)].sort_index()
    removed = pd.concat([removed, id_removed], ignore_index=True)
    return retained, removed, {"exact_duplicates_removed": int(exact.sum()), "duplicate_employee_ids_detected": source_duplicate_count}


def validate_employees(df: pd.DataFrame, boolean_invalid: dict[str, pd.Series], date_failures: dict[str, int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add reusable validation outcomes; invalid rows remain available for audit."""
    reasons = pd.Series("", index=df.index, dtype="string")
    def add(mask: pd.Series, message: str) -> None:
        nonlocal reasons
        reasons = reasons.mask(mask, reasons.mask(reasons.eq(""), "").str.cat(pd.Series(message, index=reasons.index), sep="; ").str.lstrip("; "))
    employee_id = df.get("employee_id", pd.Series(pd.NA, index=df.index)).astype("string")
    name = df.get("employee_name", pd.Series(pd.NA, index=df.index)).astype("string")
    add(employee_id.isna() | employee_id.str.strip().eq(""), "employee_id is required")
    add(name.isna() | name.str.strip().eq(""), "employee_name is required")
    if "email" in df:
        email = df.email.astype("string")
        add(email.notna() & ~email.eq("") & ~email.str.match(EMAIL_RE), "email is invalid")
    if "joining_date" not in df:
        add(pd.Series(True, index=df.index), "joining_date is required")
    else:
        add(df.joining_date.isna(), "joining_date is invalid")
        add(df.joining_date > pd.Timestamp(date.today() + timedelta(days=365)), "joining_date is too far in the future")
    for col, invalid in boolean_invalid.items():
        add(invalid.reindex(df.index, fill_value=False), f"{col} is not a boolean")
    if "onboarding_status" in df:
        add(df.onboarding_status.notna() & ~df.onboarding_status.isin(STATUS_VALUES), "onboarding_status is invalid")
    if "onboarding_status" in df and all(c in df for c in MILESTONE_COLUMNS):
        incomplete = ~df[MILESTONE_COLUMNS].fillna(False).all(axis=1)
        exception = df.get("onboarding_exception", pd.Series(False, index=df.index)).fillna(False).astype(bool)
        add(df.onboarding_status.eq("completed") & incomplete & ~exception, "completed onboarding has incomplete milestones")
    df = df.copy()
    df["validation_reasons"] = reasons
    df["passes_all_checks"] = reasons.eq("")
    return df, df.loc[~df.passes_all_checks].copy()


def _feature_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "joining_date" not in df:
        for col in ["days_since_joining", "onboarding_duration_days", "joining_month", "joining_quarter", "joining_week", "onboarding_cohort"]: df[col] = pd.NA
        return df
    joined = df.joining_date
    df["days_since_joining"] = (pd.Timestamp.today().normalize() - joined).dt.days.where(joined.notna())
    df["joining_month"] = joined.dt.strftime("%Y-%m")
    df["joining_quarter"] = joined.dt.to_period("Q").astype("string")
    df["joining_week"] = joined.dt.isocalendar().week.astype("Int64")
    df["onboarding_cohort"] = df["joining_month"]
    end = next((c for c in ("onboarding_completed_date", "onboarding_completion_date", "completed_date") if c in df), None)
    df["onboarding_duration_days"] = (df[end] - joined).dt.days.where(df[end].notna() & joined.notna()) if end else pd.NA
    return df


def validate_merge(employees: pd.DataFrame, related: pd.DataFrame, source_name: str, output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    """Audit a left join without dropping unmatched employee or related rows."""
    output_dir.mkdir(parents=True, exist_ok=True)
    employee_ids = set(employees["employee_id"].dropna().astype(str))
    related_ids = related.get("employee_id", pd.Series(dtype="string")).dropna().astype(str)
    unknown = related.loc[~related_ids.isin(employee_ids).reindex(related.index, fill_value=False)].copy()
    unmatched_employees = employees.loc[~employees["employee_id"].astype(str).isin(set(related_ids))].copy()
    unknown.to_csv(output_dir / f"unmatched_{source_name}_records.csv", index=False)
    unmatched_employees.to_csv(output_dir / f"employees_without_{source_name}.csv", index=False)
    return {"source_rows": len(related), "employee_rows": len(employees), "joined_row_count": len(employees.merge(related, on="employee_id", how="left")), "employees_without_related_records": len(unmatched_employees), "related_records_with_unknown_employee_ids": len(unknown)}


def calculate_kpis(employees: pd.DataFrame, tools: pd.DataFrame | None = None, support: pd.DataFrame | None = None) -> dict[str, Any]:
    """Calculate only evidence-backed dashboard KPIs; unavailable values are null."""
    valid = employees.loc[employees.get("passes_all_checks", True)].copy()
    total = len(valid)
    status = valid.get("onboarding_status")
    complete = status.eq("completed") if status is not None else valid.get("onboarding_complete", pd.Series(pd.NA, index=valid.index)).eq(True)
    milestones = {c.replace("_issued", "").replace("_completed", "").replace("_granted", ""): (round(float(valid[c].eq(True).mean() * 100), 1) if c in valid else None) for c in MILESTONE_COLUMNS}
    duration = valid.get("onboarding_duration_days", pd.Series(dtype="float"))
    result: dict[str, Any] = {"total_employees": total, "completion_rate": round(float(complete.mean() * 100), 1) if total and complete.notna().any() else None, "active_onboardees": int((~complete).sum()) if total and complete.notna().any() else None, "average_onboarding_speed_days": round(float(duration.dropna().mean()), 1) if duration.notna().any() else None, "milestone_completion_rates": milestones}
    if tools is not None and not tools.empty:
        numeric = [c for c in ("slack_messages", "github_commits", "jira_tickets_resolved") if c in tools]
        result["tool_adoption_rate"] = round(float((tools[numeric].fillna(0).gt(0).any(axis=1).mean()) * 100), 1) if numeric else None
    else: result["tool_adoption_rate"] = None
    result["open_support_ticket_count"] = int(support["status"].isin(["open", "in_progress"]).sum()) if support is not None and "status" in support else None
    result["department_summary"] = valid.groupby("department", dropna=False).size().to_dict() if "department" in valid else {}
    result["joining_cohort_summary"] = valid.groupby("onboarding_cohort", dropna=False).size().to_dict() if "onboarding_cohort" in valid else {}
    return result


def process_employee_dataframe(frame: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Run the complete, non-destructive employee intake quality pipeline."""
    output_dir.mkdir(parents=True, exist_ok=True)
    original = frame.copy()
    original.columns = [normalize_column_name(c) for c in original.columns]
    normalized, text_summary = normalize_text_columns(original)
    deduped, removed, duplicate_summary = _deduplicate(normalized)
    removed.to_csv(output_dir / "removed_duplicates.csv", index=False)
    parsed, date_failures = _parse_dates(deduped)
    boolean_invalid: dict[str, pd.Series] = {}
    for col in BOOLEAN_COLUMNS.intersection(parsed.columns):
        parsed[col], boolean_invalid[col] = parse_boolean(parsed[col])
    featured = _feature_dates(parsed)
    checked, failures = validate_employees(featured, boolean_invalid, date_failures)
    failures.to_csv(output_dir / "validation_failures.csv", index=False)
    for col in checked.filter(regex=r"date$").columns: checked[col] = pd.to_datetime(checked[col], errors="coerce").dt.strftime("%Y-%m-%d")
    report = {"processing_timestamp": datetime.now().isoformat(), "input_rows": len(frame), "output_rows": len(checked), "duplicate_summary": {"rows_before": len(frame), "rows_after": len(checked), **duplicate_summary}, "missing_value_summary": {c: int(v) for c, v in checked.isna().sum().items()}, "type_conversion_summary": {c: str(t) for c, t in checked.dtypes.items()}, "text_normalization_summary": text_summary, "date_parsing_failures": date_failures, "validation_failures": {"count": len(failures), "reasons": failures.validation_reasons.value_counts().to_dict()}, "merge_validation_results": {}, "derived_feature_availability": {c: c in checked.columns and checked[c].notna().any() for c in ["days_since_joining", "onboarding_duration_days", "joining_month", "joining_quarter", "joining_week", "onboarding_cohort"]}, "warnings": []}
    if "joining_date" not in original: report["warnings"].append("joining_date was not supplied; date-derived features are unavailable.")
    if len(failures): report["warnings"].append("Invalid records were retained in validation_failures.csv and excluded from active employee records.")
    return checked, report


def save_quality_report(report: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> None:
    """Persist the report in a JSON-safe form for API consumers."""
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "data_quality_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, default=str)
