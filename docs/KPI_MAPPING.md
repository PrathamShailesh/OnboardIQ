# KPI Mapping Documentation

This document explains how columns in the customer dataset map to core business Key Performance Indicators (KPIs) to drive executive and operational decision-making.

---

## 1. Monthly Revenue

- **Formula**: 
  $$\text{Monthly Revenue} = \sum (\text{amount}) \quad \text{where } \text{status} = \text{"active"} \text{ and } \text{transaction\_date} \text{ falls in the target calendar month}$$
- **Related Columns**: 
  - [amount](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (value of transaction)
  - [status](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (to ensure only active customer revenue is recognized)
  - [transaction_date](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (to attribute transaction to the correct month)
- **Business Importance**: 
  Monthly Revenue measures the raw financial health and growth rate of the business. It is the primary metric used for budgeting, forecasting, and calculating company valuation.
- **Update Frequency**: 
  Daily (aggregated monthly).

---

## 2. Sales Velocity

- **Formula**: 
  $$\text{Sales Velocity} = \frac{\text{Number of Active Accounts} \times \text{Average Deal Value} \times \text{Win Rate \%}}{\text{Average Sales Cycle Length (Days)}}$$
  *(Where Average Deal Value is the mean of `amount`, and Sales Cycle Length is calculated from differences in historical `transaction_date` status changes.)*
- **Related Columns**: 
  - [customer_id](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (count of active accounts)
  - [amount](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (average deal size)
  - [status](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (to calculate win/conversion rate)
  - [transaction_date](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (to measure conversion velocity and duration)
- **Business Importance**: 
  Sales Velocity represents how fast the pipeline is moving and how much revenue can be expected over a given timeframe. It helps sales leadership identify pipeline blockages and optimize sales rep capacity.
- **Update Frequency**: 
  Weekly.

---

## 3. Segment Revenue

- **Formula**: 
  $$\text{Segment Revenue} = \sum (\text{amount}) \quad \text{grouped by } \text{cust\_segment} \quad \text{where } \text{status} = \text{"active"}$$
- **Related Columns**: 
  - [amount](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (value of transaction)
  - [cust_segment](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (market tier e.g., Enterprise, Mid-Market, SMB)
  - [status](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (active customer filter)
- **Business Importance**: 
  Segment Revenue determines the contribution of each market tier. This guides corporate strategy on whether to focus product development and marketing acquisition spend on Enterprise clients vs. volume-based SMB strategies.
- **Update Frequency**: 
  Monthly.

---

## 4. Churn Rate

- **Formula**: 
  $$\text{Churn Rate (\%)} = \left( \frac{\text{Number of Churned Customers in Period}}{\text{Total Customers at Start of Period}} \right) \times 100$$
  *(Where a customer is churned if `flag_churn` = 1 or `status` changes from active to inactive during the period.)*
- **Related Columns**: 
  - [customer_id](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (to count unique customers)
  - [flag_churn](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (binary indicator of cancellation)
  - [status](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (account status check)
- **Business Importance**: 
  Churn Rate measures product-market fit and customer retention capability. High churn destroys growth efficiency, making it the most critical health metric for SaaS and recurring-revenue business models.
- **Update Frequency**: 
  Monthly.

---

## 5. Average Revenue Per User (ARPU) (Additional KPI)

- **Formula**: 
  $$\text{ARPU} = \frac{\text{Total Revenue in Period}}{\text{Total Count of Active Customers in Period}}$$
- **Related Columns**: 
  - [amount](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (revenue sum)
  - [customer_id](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (distinct count of active customers)
  - [status](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv) (filtering active users only)
- **Business Importance**: 
  ARPU evaluates the value of the average customer account. Monitoring ARPU trends demonstrates the effectiveness of cross-selling, upselling, packaging changes, and pricing elasticity.
- **Update Frequency**: 
  Monthly.
