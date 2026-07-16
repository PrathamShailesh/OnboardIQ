# OnboardIQ Master Data Dictionary

This master data dictionary serves as the single source of truth for the OnboardIQ customer subscription and transaction dataset. It bridges the gap between our technical database schema and business analytics, ensuring consistent reporting across teams.

---

## Dataset Overview

- **Dataset Purpose**: Tracks customer profiles, transaction histories, lifecycle statuses, and churn indicators. It powers our operational dashboards, financial reporting, and customer retention analysis.
- **Source**: Unified data streams from internal Billing Systems and CRM platforms, ingested through the OnboardIQ intake pipeline.
- **Update Frequency**: Nightly Batch ingestion (completed by 02:00 AM UTC).
- **Last Updated Date**: July 16, 2026
- **Maintained By**: OnboardIQ Analytics Engineering Team

---

## Column Documentation

Below is the detailed documentation for all columns present in the dataset.

### 1. `customer_id`
- **Data Type**: `INTEGER`
- **Business Meaning**: Unique numeric identifier assigned to each customer account upon registration.
- **Example Value**: `1`
- **Valid Values**: Positive integers greater than `0`.
- **Null Handling**: **NOT NULL**. This is the primary key; null values are invalid and rejected during ingestion.
- **Related KPIs**: [Churn Rate](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#4-churn-rate), [Monthly Revenue](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#1-monthly-revenue) (used for customer count denominators)
- **Update Frequency**: Immutable once created.
- **Business Notes**: Serves as the primary join key across support tickets, usage tools, and transaction logs.

---

### 2. `customer_name`
- **Data Type**: `VARCHAR`
- **Business Meaning**: The full name of the customer (individual or business entity).
- **Example Value**: `Alice Smith`
- **Valid Values**: Text strings.
- **Null Handling**: **Nullable**. Missing names are flagged but allowed. Defaulted to empty string if missing.
- **Related KPIs**: N/A
- **Update Frequency**: Low (updated only via profile/contract change requests).
- **Business Notes**: Often mapped from CRM inputs. In raw datasets, it may appear simply as `name`.

---

### 3. `email`
- **Data Type**: `VARCHAR`
- **Business Meaning**: Primary contact email address associated with the customer account.
- **Example Value**: `alice@example.com`
- **Valid Values**: Text string matching standard email format (`user@domain.com`).
- **Null Handling**: **Nullable**. Accounts can be created without an email if imported from legacy systems, but it is flagged as a medium quality issue.
- **Related KPIs**: [Churn Rate](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#4-churn-rate) (used for user notification mapping)
- **Update Frequency**: On-demand when updated by the customer.
- **Business Notes**: Essential for sending automated onboarding materials and renewal warnings.

---

### 4. `amount`
- **Data Type**: `DECIMAL(10,2)`
- **Business Meaning**: The monetary value of the subscription transaction in USD.
- **Example Value**: `250.00`
- **Valid Values**: Decimal numbers $\ge 0.00$.
- **Null Handling**: **Nullable** (treated as 0.00 for calculations, but flagged as a data quality issue).
- **Related KPIs**: [Monthly Revenue](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#1-monthly-revenue), [Sales Velocity](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#2-sales-velocity), [Segment Revenue](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#3-segment-revenue)
- **Update Frequency**: Appended on each billing cycle transaction.
- **Business Notes**: Represented in some raw tables as `transaction_amount`. Negative values are treated as data anomalies rather than refunds and must be investigated.

---

### 5. `status`
- **Data Type**: `VARCHAR`
- **Business Meaning**: The current subscription or account lifecycle state.
- **Example Value**: `active`
- **Valid Values**: `active`, `inactive`
- **Null Handling**: **NOT NULL** (defaults to `inactive` if unspecified).
- **Related KPIs**: [Monthly Revenue](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#1-monthly-revenue), [Churn Rate](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#4-churn-rate)
- **Update Frequency**: Real-time (changes based on invoice settlement or manual account lifecycle updates).
- **Business Notes**: Determines whether a customer is recognized in active recurring revenue calculations.

---

### 6. `transaction_date`
- **Data Type**: `DATE`
- **Business Meaning**: The date on which the transaction was processed and recorded.
- **Example Value**: `2025-01-20`
- **Valid Values**: Valid dates in `YYYY-MM-DD` format.
- **Null Handling**: **NOT NULL** (defaults to current date during database load if null).
- **Related KPIs**: [Monthly Revenue](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#1-monthly-revenue), [Sales Velocity](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#2-sales-velocity)
- **Update Frequency**: Fixed at transaction execution.
- **Business Notes**: Critical for cohort analysis, monthly revenue groupings, and assessing sales cycle durations.

---

### 7. `flag_churn`
- **Data Type**: `BOOLEAN` (stored as integer `1` or `0`)
- **Business Meaning**: A flag indicating whether the customer canceled their service/churned.
- **Example Value**: `1`
- **Valid Values**: `1` (churned), `0` (active/retained)
- **Null Handling**: **NOT NULL** (defaults to `0`).
- **Related KPIs**: [Churn Rate](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#4-churn-rate)
- **Update Frequency**: Monthly batch update or on-cancellation.
- **Business Notes**: **Ambiguous Name**. Recommend renaming to `is_churned` to align with boolean column standards and eliminate confusion.

---

### 8. `cust_segment`
- **Data Type**: `VARCHAR`
- **Business Meaning**: Customer category group based on company headcount and contract size.
- **Example Value**: `Enterprise`
- **Valid Values**: `Enterprise`, `Mid-Market`, `SMB`
- **Null Handling**: **Nullable** (defaults to `SMB`).
- **Related KPIs**: [Segment Revenue](file:///d:/kalvium/OnboardIQ/docs/KPI_MAPPING.md#3-segment-revenue)
- **Update Frequency**: Updated weekly based on customer profile sync.
- **Business Notes**: **Ambiguous Name**. Recommend renaming to `market_segment` to avoid abbreviation and clarify context.
