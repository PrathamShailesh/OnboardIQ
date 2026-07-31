# OnboardIQ Dashboard Validation Checklist

This checklist provides test scenarios to verify the dashboard accurately reflects uploaded datasets without showing misleading blank, fake, or inconsistent analytics.

## Test Scenarios

### 1. No Dataset Loaded
**Expected Behavior:**
- Overview page shows "No dataset loaded" status
- All metrics display as 0 or "Not available from this dataset"
- Recent Cohorts panel shows: "No department/cohort data is available"
- Onboarding, Tools, and Support tabs show empty states with upload prompts
- No fake data, sample metrics, or placeholder values

**Verification Steps:**
1. Start the application without uploading any dataset
2. Navigate to Overview tab
3. Verify all stat cards show:
   - Active Onboardees: 0
   - Avg. Onboarding Speed: "Not available from this dataset"
   - Tool Adoption Rate: "Not available from this dataset"
   - Open IT Support Tickets: 0
4. Verify Recent Cohorts shows empty state message
5. Navigate to Onboarding, Tools, Support tabs
6. Verify each shows appropriate empty state with upload guidance

---

### 2. Complete Valid Dataset
**Sample CSV Structure:**
```csv
employee_id,employee_name,department,joining_date,laptop_issued,access_granted,training_completed,email_setup,onboarding_complete,slack_messages,github_commits,jira_tickets_resolved
E001,John Doe,Engineering,2024-01-15,true,true,true,true,true,150,45,12
E002,Jane Smith,Marketing,2024-01-20,true,false,true,true,false,80,20,5
E003,Bob Johnson,Sales,2024-02-01,true,true,false,true,false,200,60,18
```

**Expected Behavior:**
- Active Onboardees: Count of employees where onboarding_complete = false
- Avg. Onboarding Speed: Calculated from joining_date to onboarding_complete_date (if available)
- Tool Adoption Rate: Percentage of employees with any tool activity > 0
- Recent Cohorts: Shows departments with member counts and completion rates
- Milestones reflect actual boolean values from dataset
- Tool engagement shows actual sum of tool usage fields

**Verification Steps:**
1. Upload the complete dataset
2. Verify Active Onboardees matches count of incomplete employees
3. Verify Avg. Onboarding Speed shows calculated value (e.g., "12.5 days") or "Not available" if no completion dates
4. Verify Tool Adoption Rate shows percentage (e.g., "100.0%") if tool data exists
5. Verify Recent Cohorts shows all departments with correct member counts
6. Verify milestone progress bars match actual completion counts
7. Navigate to Tools tab and verify actual tool usage data

---

### 3. Dataset Missing Tool Fields
**Sample CSV Structure:**
```csv
employee_id,employee_name,department,joining_date,laptop_issued,access_granted,training_completed,email_setup,onboarding_complete
E001,John Doe,Engineering,2024-01-15,true,true,true,true,true
E002,Jane Smith,Marketing,2024-01-20,true,false,true,true,false
```

**Expected Behavior:**
- Tool Adoption Rate: "Not available from this dataset"
- Tool engagement metrics: All show 0
- Tools tab shows empty state: "No tool usage data available"
- No random or fake tool data generated

**Verification Steps:**
1. Upload dataset without tool fields
2. Verify Tool Adoption Rate shows "Not available from this dataset"
3. Verify tool engagement metrics (Slack, GitHub, Jira) all show 0
4. Navigate to Tools tab
5. Verify empty state message: "No tool usage data available"
6. Verify empty state subtext mentions required fields

---

### 4. Dataset with Zero Access Granted
**Sample CSV Structure:**
```csv
employee_id,employee_name,department,joining_date,laptop_issued,access_granted,training_completed,email_setup,onboarding_complete
E001,John Doe,Engineering,2024-01-15,true,false,true,true,false
E002,Jane Smith,Marketing,2024-01-20,true,false,true,true,false
E003,Bob Johnson,Sales,2024-02-01,true,false,true,true,false
```

**Expected Behavior:**
- Security Access Granted milestone: 0 / total_employees
- This is a real 0 value, not missing data
- No misleading display - shows accurate 0 count
- Bottleneck analysis should identify access as a potential bottleneck

**Verification Steps:**
1. Upload dataset with access_granted = false for all employees
2. Verify Security Access Granted shows "0 / [total]" (e.g., "0 / 3")
3. Verify progress bar shows 0% completion
4. Verify this is not treated as "missing data" but as actual 0 values
5. Check bottleneck analysis for access-related delays

---

### 5. Dataset with Departments Missing
**Sample CSV Structure:**
```csv
employee_id,employee_name,joining_date,laptop_issued,access_granted,training_completed,email_setup,onboarding_complete
E001,John Doe,2024-01-15,true,true,true,true,true
E002,Jane Smith,2024-01-20,true,false,true,true,false
```

**Expected Behavior:**
- Recent Cohorts shows: "No department/cohort data is available"
- Departments default to "Unknown" or "Unassigned"
- No fake cohort data generated
- Empty state provides clear guidance

**Verification Steps:**
1. Upload dataset without department field
2. Verify Recent Cohorts panel shows empty state
3. Verify empty state message: "No department/cohort data is available"
4. Verify subtext: "Upload a dataset with department information to view cohort analytics"
5. Verify no fake cohort entries appear

---

### 6. Dataset with Support Ticket Fields
**Sample CSV Structure:**
```csv
ticket_id,employee_id,issue_type,resolution_time_hours,status,priority
TKT-0001,E001,Hardware,24,Resolved,Medium
TKT-0002,E002,Access,48,Open,High
TKT-0003,E001,Software,12,In Progress,Low
```

**Expected Behavior:**
- Open IT Support Tickets: Count of tickets with status "Open" or "In Progress"
- Support tab shows actual ticket data
- Ticket categories show distribution by issue_type
- No random or fake ticket data

**Verification Steps:**
1. Upload dataset with support ticket fields (separate from employee data)
2. Verify Open IT Support Tickets shows correct count (e.g., "2")
3. Navigate to Support tab
4. Verify ticket table shows actual uploaded tickets
5. Verify ticket categories chart shows real distribution
6. Verify no fake tickets appear

---

### 7. Failed API Response
**Expected Behavior:**
- Dashboard shows user-friendly error states
- Metrics show "Error" or "Connection error" instead of console errors
- Empty states appear with error context
- Application doesn't crash or show broken UI

**Verification Steps:**
1. Stop the backend server
2. Refresh the dashboard
3. Verify metrics show "Connection error" or similar
4. Verify no console errors crash the application
5. Verify UI remains functional
6. Restart backend and verify data loads correctly

---

## Column Mapping Validation

### Required Fields
- `employee_id` (required, must be unique)
- `employee_name` (required)

### Optional Onboarding Fields
- `department` - Used for cohort analysis
- `joining_date` - Used for onboarding speed calculation
- `laptop_issued` - Boolean milestone
- `access_granted` / `security_access_granted` - Boolean milestone
- `training_completed` - Boolean milestone
- `email_setup` - Boolean milestone
- `onboarding_complete` - Boolean milestone

### Optional Tool Fields
- `slack_messages` - Integer, default 0 if missing
- `github_commits` - Integer, default 0 if missing
- `jira_tickets_resolved` - Integer, default 0 if missing
- `slack_reactions` - Integer, default 0 if missing
- `github_prs_reviewed` - Integer, default 0 if missing

### Optional Support Ticket Fields
- `ticket_id` - String identifier
- `employee_id` - Links to employee
- `issue_type` - Category (Hardware, Software, Network, Access, Account)
- `resolution_time_hours` - Integer
- `status` - (Open, In Progress, Resolved, Closed)
- `priority` - (Low, Medium, High, Critical)

---

## Metric Calculation Validation

### Active Onboardees
**Formula:** Count of employees where `onboarding_complete = false`
**Edge Cases:**
- If no dataset: Returns 0
- If all complete: Returns 0
- If field missing: Treats as false

### Average Onboarding Speed
**Formula:** Average days between `joining_date` and `onboarding_complete_date` for completed employees
**Edge Cases:**
- If no completion dates: Returns "Not available from this dataset"
- If no completed employees: Returns "Not available from this dataset"
- Invalid dates: Excluded from calculation

### Tool Adoption Rate
**Formula:** (Employees with any tool activity > 0) / (Total employees) * 100
**Edge Cases:**
- If no tool fields: Returns "Not available from this dataset"
- If all tool values = 0: Returns "0.0%"
- If some activity: Returns actual percentage

### Open IT Support Tickets
**Formula:** Count of tickets with status "Open" or "In Progress"
**Edge Cases:**
- If no support data: Returns 0
- If no open tickets: Returns 0
- Empty support file: Returns 0

---

## Data Integrity Checks

### Boolean Field Validation
- Accepts: true/false, yes/no, 1/0, y/n (case-insensitive)
- Missing values: Default to false
- Invalid values: Default to false

### Date Field Validation
- Format: YYYY-MM-DD (auto-converted)
- Missing dates: Default to today's date for joining_date
- Invalid dates: Rejected during upload validation

### Numeric Field Validation
- Tool metrics: Default to 0 if missing or invalid
- Salary/Experience: Default to 0.0 if missing or invalid

---

## Error Handling Validation

### Upload Validation
- Missing required columns: Clear error message
- Duplicate employee IDs: Clear error message with examples
- Invalid file type: Clear error message
- Corrupted file: Clear error message

### API Error Handling
- 500 errors: User-friendly error state
- Network errors: "Connection error" message
- Timeout: Graceful degradation
- Invalid JSON: Error handling without crash

---

## Visual Validation

### Empty States
- All empty panels show clear messages
- Secondary text provides guidance
- No large blank areas without explanation
- Consistent styling across all tabs

### Metric Display
- Distinguish between: 0 (real value), "Not available" (missing data), "Error" (API failure)
- No hardcoded sample values
- No fake trends or random variations
- No placeholder people/data

### Color Coding
- Consistent use of colors for status indicators
- Accessible contrast ratios
- Clear visual hierarchy
