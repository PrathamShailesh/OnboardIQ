from pathlib import Path
import tempfile
import unittest

import pandas as pd

from scripts.onboarding_quality import calculate_kpis, process_employee_dataframe, validate_merge


class OnboardingQualityTests(unittest.TestCase):
    def test_deduplication_normalization_and_audit_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            source = pd.DataFrame({"Employee ID": ["1", "1", "2"], "Employee Name": ["  jane   doe ", "Jane Doe", "John Roe"], "Joining Date": ["2025-01-01"] * 3, "Department": ["eng", "eng", "hr"]})
            result, report = process_employee_dataframe(source, output)
            self.assertEqual(len(result), 2); self.assertEqual(result.loc[result.employee_id == "1", "employee_name"].iloc[0], "Jane Doe")
            self.assertEqual(result.loc[result.employee_id == "1", "department"].iloc[0], "Engineering")
            self.assertEqual(report["duplicate_summary"]["exact_duplicates_removed"], 1); self.assertTrue((output / "removed_duplicates.csv").exists())

    def test_invalid_dates_and_boolean_values_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result, _ = process_employee_dataframe(pd.DataFrame({"employee_id": ["1"], "employee_name": ["Jane"], "joining_date": ["not-a-date"], "laptop_issued": ["maybe"]}), Path(directory))
            self.assertFalse(result.passes_all_checks.iloc[0]); self.assertIn("joining_date is invalid", result.validation_reasons.iloc[0]); self.assertIn("laptop_issued is not a boolean", result.validation_reasons.iloc[0])

    def test_merge_validation_writes_unmatched_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory); report = validate_merge(pd.DataFrame({"employee_id": ["1", "2"]}), pd.DataFrame({"employee_id": ["1", "9"], "github_commits": [1, 4]}), "tools", output)
            self.assertEqual(report["employees_without_related_records"], 1); self.assertEqual(report["related_records_with_unknown_employee_ids"], 1); self.assertTrue((output / "unmatched_tools_records.csv").exists())

    def test_kpis_use_only_available_source_data(self) -> None:
        employees = pd.DataFrame({"passes_all_checks": [True, True], "onboarding_status": ["completed", "pending"], "laptop_issued": [True, False], "training_completed": [True, True], "access_granted": [True, False], "email_setup": [True, True], "onboarding_duration_days": [10, pd.NA]})
        kpis = calculate_kpis(employees, pd.DataFrame({"github_commits": [1, 0]}), pd.DataFrame({"status": ["open", "closed"]}))
        self.assertEqual(kpis["completion_rate"], 50.0); self.assertEqual(kpis["average_onboarding_speed_days"], 10.0); self.assertEqual(kpis["tool_adoption_rate"], 50.0); self.assertEqual(kpis["open_support_ticket_count"], 1)
