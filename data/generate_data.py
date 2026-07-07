import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_ROWS = 50

# Generate Employees data
employees_data = []
for i in range(1, NUM_ROWS + 1):
    employees_data.append({
        'ID': i,
        'Name': fake.name(),
        'Department': random.choice(['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']),
        'Joining Date': fake.date_between(start_date='-2y', end_date='today')
    })

employees_df = pd.DataFrame(employees_data)
employees_df.to_csv('data/employees.csv', index=False)

# Generate Onboarding data
onboarding_data = []
for i in range(1, NUM_ROWS + 1):
    onboarding_data.append({
        'Employee ID': i,
        'Laptop Issued': random.choice([True, False]),
        'Training Completed': random.choice([True, False]),
        'Security Access Granted': random.choice([True, False]),
        'Email Setup': random.choice([True, False]),
        'Onboarding Complete': random.choice([True, False])
    })

onboarding_df = pd.DataFrame(onboarding_data)
onboarding_df.to_csv('data/onboarding.csv', index=False)

# Generate Tools data
tools_data = []
for i in range(1, NUM_ROWS + 1):
    tools_data.append({
        'Employee ID': i,
        'Slack Messages': random.randint(0, 500),
        'GitHub Commits': random.randint(0, 100),
        'Jira Tickets Resolved': random.randint(0, 50),
        'Slack Reactions': random.randint(0, 200),
        'GitHub PRs Reviewed': random.randint(0, 30)
    })

tools_df = pd.DataFrame(tools_data)
tools_df.to_csv('data/tools.csv', index=False)

# Generate Support data
support_data = []
for i in range(1, NUM_ROWS + 1):
    resolution_time = random.randint(1, 72)  # hours
    support_data.append({
        'Ticket ID': f'TKT-{i:04d}',
        'Employee ID': i,
        'Issue Type': random.choice(['Hardware', 'Software', 'Network', 'Access', 'Account']),
        'Resolution Time (hours)': resolution_time,
        'Status': random.choice(['Open', 'In Progress', 'Resolved', 'Closed']),
        'Priority': random.choice(['Low', 'Medium', 'High', 'Critical'])
    })

support_df = pd.DataFrame(support_data)
support_df.to_csv('data/support.csv', index=False)

print("Data generation complete!")
print(f"Generated {NUM_ROWS} rows for each dataset:")
print("- data/employees.csv")
print("- data/onboarding.csv")
print("- data/tools.csv")
print("- data/support.csv")
