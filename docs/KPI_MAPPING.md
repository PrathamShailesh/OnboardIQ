# KPI Mapping Documentation

This document explains how columns in the employee onboarding dataset map to core business Key Performance Indicators (KPIs) to drive executive and operational decision-making for improving new hire productivity.

---

## 1. Onboarding Completion Rate

- **Formula**: 
  $$\text{Onboarding Completion Rate (\%)} = \left( \frac{\text{Number of Employees with Onboarding Complete = True}}{\text{Total Employees in Cohort}} \right) \times 100$$
- **Related Columns**: 
  - [Onboarding Complete](DATA_DICTIONARY.md#10-onboarding-complete) (master completion flag)
  - [Laptop Issued](DATA_DICTIONARY.md#6-laptop-issued) (hardware milestone)
  - [Training Completed](DATA_DICTIONARY.md#7-training-completed) (training milestone)
  - [Security Access Granted](DATA_DICTIONARY.md#8-security-access-granted) (access milestone)
  - [Email Setup](DATA_DICTIONARY.md#9-email-setup) (communication milestone)
  - [Joining Date](DATA_DICTIONARY.md#4-joining-date) (for cohort grouping)
- **Business Importance**: 
  Onboarding Completion Rate measures how effectively new hires are being integrated into the organization. Low completion rates indicate process bottlenecks that delay time-to-productivity and increase early attrition risk.
- **Update Frequency**: 
  Daily.

---

## 2. Time-to-Productivity

- **Formula**: 
  $$\text{Time-to-Productivity (Days)} = \text{Average}( \text{Onboarding Complete Date} - \text{Joining Date} )$$
  *(Where Onboarding Complete Date is calculated as the date when all milestone flags become True.)*
- **Related Columns**: 
  - [Onboarding Complete](DATA_DICTIONARY.md#10-onboarding-complete) (completion flag)
  - [Joining Date](DATA_DICTIONARY.md#4-joining-date) (start date)
  - [Department](DATA_DICTIONARY.md#3-department) (for departmental comparison)
- **Business Importance**: 
  Time-to-Productivity measures how long it takes for new hires to become fully operational. Reducing this metric directly impacts organizational efficiency and ROI on hiring. High variance indicates inconsistent onboarding experiences.
- **Update Frequency**: 
  Weekly.

---

## 3. Departmental Onboarding Speed

- **Formula**: 
  $$\text{Departmental Speed} = \text{Average Time-to-Productivity grouped by Department}$$
- **Related Columns**: 
  - [Department](DATA_DICTIONARY.md#3-department) (grouping dimension)
  - [Onboarding Complete](DATA_DICTIONARY.md#10-onboarding-complete) (completion flag)
  - [Joining Date](DATA_DICTIONARY.md#4-joining-date) (start date)
- **Business Importance**: 
  Identifies which departments have efficient onboarding processes versus those experiencing bottlenecks. Enables targeted process improvements and resource allocation to underperforming departments.
- **Update Frequency**: 
  Weekly.

---

## 4. Hardware Bottleneck Rate

- **Formula**: 
  $$\text{Hardware Bottleneck Rate (\%)} = \left( \frac{\text{Employees with Laptop Issued = False and Days Since Joining > 7}}{\text{Total Employees}} \right) \times 100$$
- **Related Columns**: 
  - [Laptop Issued](DATA_DICTIONARY.md#6-laptop-issued) (hardware status)
  - [Joining Date](DATA_DICTIONARY.md#4-joining-date) (to calculate days since joining)
  - [Issue Type](DATA_DICTIONARY.md#19-issue-type) (from support tickets, filter = 'Hardware')
- **Business Importance**: 
  Hardware delays are a critical blocker for remote and hybrid work. High bottleneck rates indicate IT procurement or asset management issues that need immediate attention.
- **Update Frequency**: 
  Daily.

---

## 5. Access Bottleneck Rate

- **Formula**: 
  $$\text{Access Bottleneck Rate (\%)} = \left( \frac{\text{Employees with Security Access Granted = False and Days Since Joining > 5}}{\text{Total Employees}} \right) \times 100$$
- **Related Columns**: 
  - [Security Access Granted](DATA_DICTIONARY.md#8-security-access-granted) (access status)
  - [Joining Date](DATA_DICTIONARY.md#4-joining-date) (to calculate days since joining)
  - [Issue Type](DATA_DICTIONARY.md#19-issue-type) (from support tickets, filter = 'Access')
- **Business Importance**: 
  Access delays prevent employees from using critical systems and tools. High rates indicate IT/Security process inefficiencies that significantly impact productivity.
- **Update Frequency**: 
  Daily.

---

## 6. Tool Adoption Rate

- **Formula**: 
  $$\text{Tool Adoption Rate (\%)} = \left( \frac{\text{Employees with (Slack Messages > 0 OR GitHub Commits > 0 OR Jira Tickets > 0)}}{\text{Total Employees}} \right) \times 100$$
- **Related Columns**: 
  - [Slack Messages](DATA_DICTIONARY.md#12-slack-messages) (collaboration activity)
  - [GitHub Commits](DATA_DICTIONARY.md#13-github-commits) (development activity)
  - [Jira Tickets Resolved](DATA_DICTIONARY.md#14-jira-tickets-resolved) (task management activity)
  - [Department](DATA_DICTIONARY.md#3-department) (for role-based analysis)
- **Business Importance**: 
  Tool Adoption Rate measures how quickly new hires begin using internal tools. Low adoption may indicate training gaps, access issues, or tool complexity. High adoption correlates with faster time-to-productivity.
- **Update Frequency**: 
  Daily.

---

## 7. Collaboration Index

- **Formula**: 
  $$\text{Collaboration Index} = \frac{\text{Average Slack Messages} + \text{Average Slack Reactions}}{\text{Department Baseline}}$$
- **Related Columns**: 
  - [Slack Messages](DATA_DICTIONARY.md#12-slack-messages) (communication volume)
  - [Slack Reactions](DATA_DICTIONARY.md#15-slack-reactions) (social engagement)
  - [Department](DATA_DICTIONARY.md#3-department) (for baseline comparison)
- **Business Importance**: 
  Collaboration Index measures how well new hires are integrating into team communication patterns. Low scores may indicate social isolation, onboarding support gaps, or cultural fit issues.
- **Update Frequency**: 
  Weekly.

---

## 8. Development Velocity

- **Formula**: 
  $$\text{Development Velocity} = \frac{\text{Average GitHub Commits} + \text{Average GitHub PRs Reviewed}}{\text{Engineering Role Baseline}}$$
- **Related Columns**: 
  - [GitHub Commits](DATA_DICTIONARY.md#13-github-commits) (code contribution)
  - [GitHub PRs Reviewed](DATA_DICTIONARY.md#16-github-prs-reviewed) (code review participation)
  - [Department](DATA_DICTIONARY.md#3-department) (filter = 'Engineering')
- **Business Importance**: 
  Development Velocity measures how quickly engineering hires begin contributing to codebases. Low velocity indicates onboarding delays in development environment setup, access provisioning, or technical training.
- **Update Frequency**: 
  Weekly.

---

## 9. Productivity Index

- **Formula**: 
  $$\text{Productivity Index} = \frac{\text{Average Jira Tickets Resolved}}{\text{Role-Specific Baseline}}$$
- **Related Columns**: 
  - [Jira Tickets Resolved](DATA_DICTIONARY.md#14-jira-tickets-resolved) (task completion)
  - [Department](DATA_DICTIONARY.md#3-department) (for role-specific baselines)
- **Business Importance**: 
  Productivity Index measures task completion velocity relative to role expectations. Helps identify which departments or roles have effective onboarding for task management tools and processes.
- **Update Frequency**: 
  Weekly.

---

## 10. Support Ticket Volume

- **Formula**: 
  $$\text{Support Ticket Volume} = \text{Count of tickets where Status in ['Open', 'In Progress']}$$
- **Related Columns**: 
  - [Status](DATA_DICTIONARY.md#21-status) (ticket status filter)
  - [Employee ID](DATA_DICTIONARY.md#18-employee-id) (to count per employee)
  - [Joining Date](DATA_DICTIONARY.md#4-joining-date) (to filter recent hires)
- **Business Importance**: 
  High support ticket volume from new hires indicates onboarding process issues, inadequate documentation, or tool complexity. Tracking this helps identify systemic problems affecting multiple employees.
- **Update Frequency**: 
  Daily.

---

## 11. Average Resolution Time

- **Formula**: 
  $$\text{Average Resolution Time (Hours)} = \text{Average}( \text{Resolution Time (hours)} ) \text{ where Status = 'Resolved'}$$
- **Related Columns**: 
  - [Resolution Time (hours)](DATA_DICTIONARY.md#20-resolution-time-hours) (time metric)
  - [Status](DATA_DICTIONARY.md#21-status) (filter resolved tickets)
  - [Issue Type](DATA_DICTIONARY.md#19-issue-type) (for category analysis)
- **Business Importance**: 
  Long resolution times indicate IT support bottlenecks that delay onboarding. High resolution times for specific issue types highlight process areas needing improvement.
- **Update Frequency**: 
  Weekly.

---

## 12. Issue Type Distribution

- **Formula**: 
  $$\text{Issue Type Distribution} = \text{Count of tickets grouped by Issue Type}$$
- **Related Columns**: 
  - [Issue Type](DATA_DICTIONARY.md#19-issue-type) (category dimension)
  - [Priority](DATA_DICTIONARY.md#22-priority) (severity context)
- **Business Importance**: 
  Identifies the most common onboarding friction points. High concentrations in specific categories (e.g., Hardware, Access) indicate where to focus process improvements and resource allocation.
- **Update Frequency**: 
  Weekly.

---

## 13. Critical Issue Rate

- **Formula**: 
  $$\text{Critical Issue Rate (\%)} = \left( \frac{\text{Tickets with Priority = 'Critical' or 'High'}}{\text{Total Tickets}} \right) \times 100$$
- **Related Columns**: 
  - [Priority](DATA_DICTIONARY.md#22-priority) (severity level)
  - [Issue Type](DATA_DICTIONARY.md#19-issue-type) (category context)
- **Business Importance**: 
  High critical issue rates indicate severe onboarding blockers that prevent employees from working. This metric triggers immediate intervention and process review to prevent widespread productivity impact.
- **Update Frequency**: 
  Daily.
