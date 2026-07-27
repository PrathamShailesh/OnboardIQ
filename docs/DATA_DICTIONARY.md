# OnboardIQ Master Data Dictionary

This master data dictionary serves as the single source of truth for the OnboardIQ employee onboarding dataset. It bridges the gap between our technical database schema and business analytics, ensuring consistent reporting across teams.

---

## Dataset Overview

- **Dataset Purpose**: Tracks employee profiles, onboarding progress, internal tool usage, and IT support ticket history. It powers operational dashboards, productivity analysis, and onboarding bottleneck identification.
- **Source**: Unified data streams from HR systems, IT asset management, collaboration tools (Slack, GitHub, Jira), and IT helpdesk systems, ingested through the OnboardIQ intake pipeline.
- **Update Frequency**: Real-time for tool usage, daily for onboarding progress, nightly batch for support tickets.
- **Last Updated Date**: July 27, 2026
- **Maintained By**: OnboardIQ Analytics Engineering Team

---

## Dataset Files

### 1. Employees Dataset (`employees.csv`)
Primary employee information and demographics.

### 2. Onboarding Dataset (`onboarding.csv`)
Tracks onboarding milestone completion status for each employee.

### 3. Tools Dataset (`tools.csv`)
Tracks engagement metrics across internal collaboration and development tools.

### 4. Support Dataset (`support.csv`)
IT support ticket history and resolution metrics.

---

## Column Documentation

### Employees Dataset Columns

#### 1. `ID`
- **Data Type**: `INTEGER`
- **Business Meaning**: Unique numeric identifier assigned to each employee upon joining.
- **Example Value**: `1`
- **Valid Values**: Positive integers greater than `0`.
- **Null Handling**: **NOT NULL**. This is the primary key; null values are invalid and rejected during ingestion.
- **Related KPIs**: [Onboarding Completion Rate](KPI_MAPPING.md#1-onboarding-completion-rate), [Time-to-Productivity](KPI_MAPPING.md#2-time-to-productivity)
- **Update Frequency**: Immutable once created.
- **Business Notes**: Serves as the primary join key across onboarding, tools, and support datasets.

---

#### 2. `Name`
- **Data Type**: `VARCHAR`
- **Business Meaning**: The full name of the employee.
- **Example Value**: `Alice Smith`
- **Valid Values**: Text strings.
- **Null Handling**: **Nullable**. Missing names are flagged but allowed. Defaulted to empty string if missing.
- **Related KPIs**: N/A
- **Update Frequency**: Low (updated only via HR profile changes).
- **Business Notes**: Often mapped from HRIS inputs. In raw datasets, it may appear as `employee_name`.

---

#### 3. `Department`
- **Data Type**: `VARCHAR`
- **Business Meaning**: The organizational department the employee belongs to.
- **Example Value**: `Engineering`
- **Valid Values**: `Engineering`, `Marketing`, `Sales`, `HR`, `Finance`, `Operations`
- **Null Handling**: **Nullable**. Defaulted to `Unassigned` if missing.
- **Related KPIs**: [Departmental Onboarding Speed](KPI_MAPPING.md#3-departmental-onboarding-speed)
- **Update Frequency**: Updated on department transfers.
- **Business Notes**: Used for cohort analysis and department-level bottleneck identification.

---

#### 4. `Joining Date`
- **Data Type**: `DATE`
- **Business Meaning**: The date on which the employee officially joined the organization.
- **Example Value**: `2025-01-20`
- **Valid Values**: Valid dates in `YYYY-MM-DD` format.
- **Null Handling**: **NOT NULL** (defaults to current date during database load if null).
- **Related KPIs**: [Time-to-Productivity](KPI_MAPPING.md#2-time-to-productivity), [Onboarding Completion Rate](KPI_MAPPING.md#1-onboarding-completion-rate)
- **Update Frequency**: Immutable once set.
- **Business Notes**: Critical for calculating onboarding duration, cohort analysis, and measuring time-to-productivity metrics.

---

### Onboarding Dataset Columns

#### 5. `Employee ID`
- **Data Type**: `INTEGER`
- **Business Meaning**: Foreign key referencing the employee in the employees dataset.
- **Example Value**: `1`
- **Valid Values**: Positive integers matching employee IDs.
- **Null Handling**: **NOT NULL**. Must reference a valid employee.
- **Related KPIs**: All onboarding KPIs
- **Update Frequency**: Immutable once created.
- **Business Notes**: Join key for linking onboarding progress to employee profiles.

---

#### 6. `Laptop Issued`
- **Data Type**: `BOOLEAN`
- **Business Meaning**: Indicates whether the employee has been issued a company laptop.
- **Example Value**: `True`
- **Valid Values**: `True` (issued), `False` (not issued)
- **Null Handling**: **NOT NULL** (defaults to `False`).
- **Related KPIs**: [Onboarding Completion Rate](KPI_MAPPING.md#1-onboarding-completion-rate), [Hardware Bottleneck Rate](KPI_MAPPING.md#4-hardware-bottleneck-rate)
- **Update Frequency**: Updated when laptop is issued.
- **Business Notes**: Critical hardware milestone; delays here significantly impact time-to-productivity.

---

#### 7. `Training Completed`
- **Data Type**: `BOOLEAN`
- **Business Meaning**: Indicates whether the employee has completed mandatory onboarding training.
- **Example Value**: `True`
- **Valid Values**: `True` (completed), `False` (not completed)
- **Null Handling**: **NOT NULL** (defaults to `False`).
- **Related KPIs**: [Onboarding Completion Rate](KPI_MAPPING.md#1-onboarding-completion-rate)
- **Update Frequency**: Updated when training modules are completed.
- **Business Notes**: Training completion is often a prerequisite for system access and tool adoption.

---

#### 8. `Security Access Granted`
- **Data Type**: `BOOLEAN`
- **Business Meaning**: Indicates whether the employee has been granted necessary security access and credentials.
- **Example Value**: `True`
- **Valid Values**: `True` (granted), `False` (not granted)
- **Null Handling**: **NOT NULL** (defaults to `False`).
- **Related KPIs**: [Onboarding Completion Rate](KPI_MAPPING.md#1-onboarding-completion-rate), [Access Bottleneck Rate](KPI_MAPPING.md#5-access-bottleneck-rate)
- **Update Frequency**: Updated when access is provisioned.
- **Business Notes**: Security access includes VPN, SSO, and system-specific credentials. Delays here block productivity.

---

#### 9. `Email Setup`
- **Data Type**: `BOOLEAN`
- **Business Meaning**: Indicates whether the employee's corporate email account has been configured.
- **Example Value**: `True`
- **Valid Values**: `True` (configured), `False` (not configured)
- **Null Handling**: **NOT NULL** (defaults to `False`).
- **Related KPIs**: [Onboarding Completion Rate](KPI_MAPPING.md#1-onboarding-completion-rate)
- **Update Frequency**: Updated when email is provisioned.
- **Business Notes**: Email setup is typically the first communication milestone; delays impact all subsequent coordination.

---

#### 10. `Onboarding Complete`
- **Data Type**: `BOOLEAN`
- **Business Meaning**: Overall flag indicating whether all onboarding milestones are complete.
- **Example Value**: `True`
- **Valid Values**: `True` (complete), `False` (incomplete)
- **Null Handling**: **NOT NULL** (defaults to `False`).
- **Related KPIs**: [Onboarding Completion Rate](KPI_MAPPING.md#1-onboarding-completion-rate), [Time-to-Productivity](KPI_MAPPING.md#2-time-to-productivity)
- **Update Frequency**: Updated when all sub-milestones are complete.
- **Business Notes**: This is the master onboarding flag; typically set automatically when all sub-milestones are `True`.

---

### Tools Dataset Columns

#### 11. `Employee ID`
- **Data Type**: `INTEGER`
- **Business Meaning**: Foreign key referencing the employee in the employees dataset.
- **Example Value**: `1`
- **Valid Values**: Positive integers matching employee IDs.
- **Null Handling**: **NOT NULL**. Must reference a valid employee.
- **Related KPIs**: [Tool Adoption Rate](KPI_MAPPING.md#6-tool-adoption-rate)
- **Update Frequency**: Immutable once created.
- **Business Notes**: Join key for linking tool usage to employee profiles.

---

#### 12. `Slack Messages`
- **Data Type**: `INTEGER`
- **Business Meaning**: Number of Slack messages sent by the employee in the first 30 days.
- **Example Value**: `234`
- **Valid Values**: Non-negative integers.
- **Null Handling**: **Nullable** (treated as `0` for calculations).
- **Related KPIs**: [Tool Adoption Rate](KPI_MAPPING.md#6-tool-adoption-rate), [Collaboration Index](KPI_MAPPING.md#7-collaboration-index)
- **Update Frequency**: Daily aggregation.
- **Business Notes**: High message count indicates active collaboration; very low counts may indicate access issues or disengagement.

---

#### 13. `GitHub Commits`
- **Data Type**: `INTEGER`
- **Business Meaning**: Number of GitHub commits made by the employee in the first 30 days.
- **Example Value**: `48`
- **Valid Values**: Non-negative integers.
- **Null Handling**: **Nullable** (treated as `0` for calculations).
- **Related KPIs**: [Tool Adoption Rate](KPI_MAPPING.md#6-tool-adoption-rate), [Development Velocity](KPI_MAPPING.md#8-development-velocity)
- **Update Frequency**: Daily aggregation.
- **Business Notes**: Relevant for engineering roles; zero commits for engineers may indicate access issues or onboarding delays.

---

#### 14. `Jira Tickets Resolved`
- **Data Type**: `INTEGER`
- **Business Meaning**: Number of Jira tickets resolved by the employee in the first 30 days.
- **Example Value**: `18`
- **Valid Values**: Non-negative integers.
- **Null Handling**: **Nullable** (treated as `0` for calculations).
- **Related KPIs**: [Tool Adoption Rate](KPI_MAPPING.md#6-tool-adoption-rate), [Productivity Index](KPI_MAPPING.md#9-productivity-index)
- **Update Frequency**: Daily aggregation.
- **Business Notes**: Indicates task completion and project management engagement; varies significantly by role.

---

#### 15. `Slack Reactions`
- **Data Type**: `INTEGER`
- **Business Meaning**: Number of Slack reactions given/received by the employee in the first 30 days.
- **Example Value**: `89`
- **Valid Values**: Non-negative integers.
- **Null Handling**: **Nullable** (treated as `0` for calculations).
- **Related KPIs**: [Collaboration Index](KPI_MAPPING.md#7-collaboration-index)
- **Update Frequency**: Daily aggregation.
- **Business Notes**: Indicates social integration and team engagement.

---

#### 16. `GitHub PRs Reviewed`
- **Data Type**: `INTEGER`
- **Business Meaning**: Number of GitHub pull requests reviewed by the employee in the first 30 days.
- **Example Value**: `12`
- **Valid Values**: Non-negative integers.
- **Null Handling**: **Nullable** (treated as `0` for calculations).
- **Related KPIs**: [Development Velocity](KPI_MAPPING.md#8-development-velocity)
- **Update Frequency**: Daily aggregation.
- **Business Notes**: Indicates code review participation and team collaboration for engineering roles.

---

### Support Dataset Columns

#### 17. `Ticket ID`
- **Data Type**: `VARCHAR`
- **Business Meaning**: Unique identifier for the IT support ticket.
- **Example Value**: `TKT-0001`
- **Valid Values**: Alphanumeric string following ticket ID format.
- **Null Handling**: **NOT NULL**. This is the primary key.
- **Related KPIs**: [Support Ticket Volume](KPI_MAPPING.md#10-support-ticket-volume), [Average Resolution Time](KPI_MAPPING.md#11-average-resolution-time)
- **Update Frequency**: Immutable once created.
- **Business Notes**: Used for tracking and referencing support requests.

---

#### 18. `Employee ID`
- **Data Type**: `INTEGER`
- **Business Meaning**: Foreign key referencing the employee who submitted the ticket.
- **Example Value**: `1`
- **Valid Values**: Positive integers matching employee IDs.
- **Null Handling**: **NOT NULL**. Must reference a valid employee.
- **Related KPIs**: [Support Ticket Volume](KPI_MAPPING.md#10-support-ticket-volume)
- **Update Frequency**: Immutable once created.
- **Business Notes**: Join key for linking support tickets to employee profiles.

---

#### 19. `Issue Type`
- **Data Type**: `VARCHAR`
- **Business Meaning**: Category of the IT support issue.
- **Example Value**: `Hardware`
- **Valid Values**: `Hardware`, `Software`, `Network`, `Access`, `Account`
- **Null Handling**: **NOT NULL** (defaults to `Other` if unspecified).
- **Related KPIs**: [Issue Type Distribution](KPI_MAPPING.md#12-issue-type-distribution)
- **Update Frequency**: Immutable once created.
- **Business Notes**: Used for identifying common onboarding friction points and IT resource allocation.

---

#### 20. `Resolution Time (hours)`
- **Data Type**: `INTEGER`
- **Business Meaning**: Time taken to resolve the support ticket, in hours.
- **Example Value**: `24`
- **Valid Values**: Positive integers.
- **Null Handling**: **Nullable** (treated as `0` for open tickets).
- **Related KPIs**: [Average Resolution Time](KPI_MAPPING.md#11-average-resolution-time)
- **Update Frequency**: Updated when ticket is resolved.
- **Business Notes**: Long resolution times indicate IT bottlenecks that impact onboarding speed.

---

#### 21. `Status`
- **Data Type**: `VARCHAR`
- **Business Meaning**: Current status of the support ticket.
- **Example Value**: `Resolved`
- **Valid Values**: `Open`, `In Progress`, `Resolved`, `Closed`
- **Null Handling**: **NOT NULL** (defaults to `Open`).
- **Related KPIs**: [Support Ticket Volume](KPI_MAPPING.md#10-support-ticket-volume)
- **Update Frequency**: Updated as ticket status changes.
- **Business Notes**: Open and In Progress tickets indicate active onboarding blockers.

---

#### 22. `Priority`
- **Data Type**: `VARCHAR`
- **Business Meaning**: Priority level assigned to the support ticket.
- **Example Value**: `High`
- **Valid Values**: `Low`, `Medium`, `High`, `Critical`
- **Null Handling**: **NOT NULL** (defaults to `Medium`).
- **Related KPIs**: [Critical Issue Rate](KPI_MAPPING.md#13-critical-issue-rate)
- **Update Frequency**: Can be updated during ticket lifecycle.
- **Business Notes**: High and Critical priority tickets indicate severe onboarding blockers requiring immediate attention.
