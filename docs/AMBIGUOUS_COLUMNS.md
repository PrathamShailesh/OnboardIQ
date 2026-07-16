# Ambiguous Columns Analysis

This document identifies poorly named or ambiguous columns in our dataset, highlights the operational risks of their current naming, and proposes new, standardized business-friendly names to prevent analyst error.

---

## 1. Original Column: `flag_churn`

### Why it is ambiguous
- **Technical vs. Business Duality**: The prefix `flag_` is a technical implementation detail (suggesting a boolean or bitwise field) rather than a clear business concept.
- **Directional Ambiguity**: It is unclear whether a value of `1` (or `True`) means the customer *is active* and flagged for monitoring, or if they have *already canceled* (churned). Inverted interpretations can lead to completely backward churn reports.

### Correct Business Meaning
This column indicates whether a customer has canceled their subscription or service during the reporting window.

### Business Interpretation
- `1` / `True`: The customer has officially terminated their relationship with the company (churned).
- `0` / `False`: The customer remains an active subscriber.

### Proposed New Column Name
`is_churned`

### Risk if Misunderstood
If an analyst assumes `flag_churn = 1` refers to "active customers flagged for churn risk" (retention candidates) instead of "completed cancellations", they will invert the churn rate. This could lead executives to believe retention is high when it is actually low, or vice versa, resulting in disastrous strategic decisions and misallocated marketing/retention budget.

---

## 2. Original Column: `cust_segment`

### Why it is ambiguous
- **Abbreviation Usage**: The abbreviation `cust_` unnecessarily shortens "customer" and creates inconsistency with other columns (like `customer_name`).
- **Criteria Ambiguity**: The term `segment` does not clarify the classification criteria. It could refer to behavioral segments, geographic segments, product usage tiers, or firmographic market sizes (SMB/Enterprise).

### Correct Business Meaning
The classification of a customer based on company size and contract value (Enterprise, Mid-Market, SMB).

### Business Interpretation
- `Enterprise`: Large scale corporations with high-contract values.
- `Mid-Market`: Medium-sized businesses with moderate-contract values.
- `SMB`: Small and Medium Businesses with lower, volume-oriented values.

### Proposed New Column Name
`market_segment`

### Risk if Misunderstood
Analysts might mix up this column with marketing campaign segments or geographic regions. For instance, if segment revenue calculations group users by marketing tier instead of enterprise-size tier, the company may over-invest in products tailored for small businesses thinking they are driving enterprise-level revenue.
