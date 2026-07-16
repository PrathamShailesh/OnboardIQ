# Column Relationships & Analytical Insights

This document describes how multiple columns in the customer dataset interact to build complex metrics, reveal underlying business trends, and generate strategic insights.

---

## 1. Revenue per Customer (ARPU)

### Relationship Title
Average Revenue Per User (ARPU) / Revenue Concentration

### Business Definition
The relationship between customer identifiers (`customer_id`), transaction values (`amount`), and account status (`status`). It determines how much revenue is generated on average per active client account.

### Why it Matters
This relationship helps businesses understand customer unit economics. If a small group of customers generates the vast majority of revenue, the business has high "revenue concentration risk" (meaning the loss of a single customer could severely damage revenue). If ARPU is low across a high number of users, the business model relies heavily on volume and scale.

### Example Insight
By filtering `status = 'active'` and grouping `amount` by `customer_id`, we might discover that 80% of monthly revenue is driven by just 10% of customers, indicating a need for a dedicated account management strategy for high-value clients.

### Related Columns
- [customer_id](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)
- [amount](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)
- [status](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)

---

## 2. Churn by Segment

### Relationship Title
Customer Churn Rate by Market Segment

### Business Definition
The interaction of customer market tier (`cust_segment`) with cancellation flags (`flag_churn`). It calculates the proportion of lost accounts within each target market.

### Why it Matters
Different customer segments have different needs, price sensitivities, and onboarding experiences. Measuring churn at the aggregate level masks segment-specific failures. Identifying which market segment is losing customers fastest allows targeted intervention.

### Example Insight
An analysis reveals that SMB churn is 15% while Enterprise churn is only 1%. This indicates that the product or onboarding experience is likely too complex for small businesses who lack dedicated IT setup teams, highlighting a need for simplified onboarding or a self-service training model.

### Related Columns
- [cust_segment](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)
- [flag_churn](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)
- [customer_id](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)

---

## 3. Revenue Velocity

### Relationship Title
Time-to-Revenue / Revenue Realization Speed

### Business Definition
The relationship between transaction dates (`transaction_date`), contract or deal values (`amount`), and account creation or onboarding status. It tracks the speed and timing at which opportunities convert to cash.

### Why it Matters
Cash flow is critical. A high contract value is less valuable if it takes 180 days to convert into active revenue. Measuring the duration between account initialization and active `transaction_date` shows how efficiently the sales and onboarding teams move deals through the pipeline.

### Example Insight
Evaluating `amount` over `transaction_date` shows that while Enterprise deals are 10x larger than SMB deals, their time-to-revenue is 5x longer, helping finance plan monthly working capital requirements and sales teams set realistic quotas.

### Related Columns
- [amount](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)
- [transaction_date](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)
- [status](file:///d:/kalvium/OnboardIQ/docs/data_dictionary.csv)
