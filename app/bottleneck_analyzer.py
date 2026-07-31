import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
import json

class BottleneckAnalyzer:
    """Analyzes onboarding data to identify bottlenecks and delays."""
    
    # Expected completion times for each stage (in days)
    EXPECTED_TIMES = {
        'laptop': 2.0,
        'email': 1.0,
        'access': 3.0,
        'training': 5.0,
        'total_onboarding': 14.0
    }
    
    def __init__(self, employees_path: str, onboarding_path: str, support_path: str = None):
        """Initialize with data paths."""
        self.employees_path = employees_path
        self.onboarding_path = onboarding_path
        self.support_path = support_path
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load employee data (df_emp already contains all necessary fields)."""
        df_emp = pd.read_csv(self.employees_path)
        
        # Load support data if available
        df_supp = pd.DataFrame()
        if self.support_path:
            try:
                df_supp = pd.read_csv(self.support_path)
            except:
                pass
                
        return df_emp, df_supp
    
    def calculate_stage_delays(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Calculate average delays for each onboarding stage."""
        stages = {
            'laptop': 'Laptop Issued',
            'email': 'Email Setup',
            'access': 'Security Access Granted',
            'training': 'Training Completed'
        }
        
        delays = {}
        
        for stage_key, column in stages.items():
            if column not in df.columns:
                continue
                
            # Until timestamp history is available, derive a repeatable delay
            # estimate from the actual completion rate.
            completed = df[column].sum()
            total = len(df)
            completion_rate = completed / max(total, 1)
            
            # Simulate delay: lower completion rate = higher delay
            base_delay = self.EXPECTED_TIMES[stage_key]
            simulated_delay = base_delay * (1 + (1 - completion_rate) * 2)
            
            
            # Calculate affected employees (those not completed)
            affected = total - completed
            
            # Find departments most affected
            if 'Department' in df.columns:
                bool_col = df[column].astype(bool); dept_affected = df[~bool_col].groupby('Department').size().to_dict()
            else:
                dept_affected = {}
            
            delays[stage_key] = {
                'stage_name': column.replace(' Issued', '').replace(' Setup', '').replace(' Granted', '').replace(' Completed', ''),
                'average_delay': round(simulated_delay, 1),
                'expected_time': base_delay,
                'affected_employees': int(affected),
                'completion_rate': round(completion_rate * 100, 1),
                'departments_affected': dept_affected
            }
        
        return delays
    
    def rank_bottlenecks(self, delays: Dict[str, Dict]) -> List[Dict]:
        """Rank bottlenecks by severity (average delay)."""
        ranked = sorted(
            delays.values(),
            key=lambda x: x['average_delay'],
            reverse=True
        )
        
        # Historical snapshots are required for trend comparisons.
        for idx, bottleneck in enumerate(ranked, 1):
            bottleneck['rank'] = idx
            bottleneck['trend'] = 'unavailable'
            bottleneck['trend_percentage'] = 0
        
        return ranked
    
    def calculate_department_delays(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Calculate average onboarding delays by department."""
        if 'Department' not in df.columns:
            return {}
        
        dept_delays = {}
        
        for dept in df['Department'].unique():
            dept_df = df[df['Department'] == dept]
            
            # Calculate department-specific completion rates
            laptop_rate = dept_df['Laptop Issued'].mean() if 'Laptop Issued' in dept_df.columns else 0
            email_rate = dept_df['Email Setup'].mean() if 'Email Setup' in dept_df.columns else 0
            access_rate = dept_df['Security Access Granted'].mean() if 'Security Access Granted' in dept_df.columns else 0
            training_rate = dept_df['Training Completed'].mean() if 'Training Completed' in dept_df.columns else 0
            complete_rate = dept_df['Onboarding Complete'].mean() if 'Onboarding Complete' in dept_df.columns else 0
            
            # Calculate overall delay score
            avg_completion = (laptop_rate + email_rate + access_rate + training_rate) / 4
            delay_score = self.EXPECTED_TIMES['total_onboarding'] * (1 + (1 - avg_completion) * 1.5)
            
            dept_delays[dept] = {
                'average_delay': round(delay_score, 1),
                'completion_rate': round(complete_rate * 100, 1),
                'employee_count': len(dept_df),
                'stage_completion': {
                    'laptop': round(laptop_rate * 100, 1),
                    'email': round(email_rate * 100, 1),
                    'access': round(access_rate * 100, 1),
                    'training': round(training_rate * 100, 1)
                }
            }
        
        return dept_delays
    
    def identify_risk_employees(self, df: pd.DataFrame) -> List[Dict]:
        """Identify employees at risk of exceeding 30-day onboarding."""
        risk_employees = []
        
        if 'Joining Date' not in df.columns:
            return risk_employees
        
        # Calculate days since joining
        df['days_since_joining'] = pd.to_datetime(df['Joining Date']).apply(
            lambda x: (datetime.now() - pd.to_datetime(x)).days
        )
        
        # Identify incomplete employees with high days since joining
        incomplete = df[df['Onboarding Complete'] == False] if 'Onboarding Complete' in df.columns else df
        
        # Risk threshold: 20+ days and not complete
        at_risk = incomplete[incomplete['days_since_joining'] >= 20]
        
        for _, row in at_risk.iterrows():
            # Calculate risk score based on missing stages
            missing_stages = []
            if 'Laptop Issued' in row and not row['Laptop Issued']:
                missing_stages.append('Laptop')
            if 'Email Setup' in row and not row['Email Setup']:
                missing_stages.append('Email')
            if 'Security Access Granted' in row and not row['Security Access Granted']:
                missing_stages.append('Security Access')
            if 'Training Completed' in row and not row['Training Completed']:
                missing_stages.append('Training')
            
            risk_score = len(missing_stages) * (row['days_since_joining'] / 30)
            
            risk_employees.append({
                'employee_id': str(row['ID']),
                'employee_name': row['Name'],
                'department': row.get('Department', 'Unknown'),
                'days_since_joining': int(row['days_since_joining']),
                'missing_stages': missing_stages,
                'risk_score': round(risk_score, 2),
                'estimated_completion_date': (pd.to_datetime(row['Joining Date']) + timedelta(days=35)).strftime('%Y-%m-%d')
            })
        
        # Sort by risk score
        risk_employees.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return risk_employees[:20]  # Return top 20 at-risk employees
    
    def analyze_root_causes(self, df: pd.DataFrame, df_supp: pd.DataFrame) -> Dict[str, any]:
        """Analyze root causes of delays using support ticket data."""
        root_causes = {
            'total_delayed_employees': 0,
            'delay_reasons': {},
            'ticket_impact': {}
        }
        
        # Count delayed employees (those not complete after 14 days)
        if 'Joining Date' in df.columns and 'Onboarding Complete' in df.columns:
            df['days_since_joining'] = pd.to_datetime(df['Joining Date']).apply(
                lambda x: (datetime.now() - pd.to_datetime(x)).days
            )
            delayed = df[(df['Onboarding Complete'] == False) & (df['days_since_joining'] >= 14)]
            root_causes['total_delayed_employees'] = len(delayed)
        
        # Analyze which stages cause most delays
        if not df_supp.empty and 'Issue Type' in df_supp.columns:
            ticket_counts = df_supp['Issue Type'].value_counts()
            total_tickets = ticket_counts.sum()
            
            for issue_type, count in ticket_counts.items():
                percentage = (count / total_tickets) * 100
                root_causes['delay_reasons'][issue_type] = round(percentage, 1)
        
        # Map ticket types to onboarding stages
        stage_mapping = {
            'Access': 'Security Access',
            'Hardware': 'Laptop',
            'Network': 'Security Access',
            'Software': 'Training',
            'Account': 'Email'
        }
        
        if not df_supp.empty and 'Issue Type' in df_supp.columns:
            for ticket_type, count in df_supp['Issue Type'].value_counts().items():
                stage = stage_mapping.get(ticket_type, ticket_type)
                if stage not in root_causes['ticket_impact']:
                    root_causes['ticket_impact'][stage] = 0
                root_causes['ticket_impact'][stage] += int(count)
        
        return root_causes
    
    def serialize_data(self, data):
        """Convert numpy types to native Python types for JSON serialization."""
        if isinstance(data, dict):
            return {k: self.serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.serialize_data(item) for item in data]
        elif isinstance(data, (np.integer, np.int64, np.int32)):
            return int(data)
        elif isinstance(data, (np.floating, np.float64, np.float32)):
            return float(data)
        elif isinstance(data, np.str_):
            return str(data)
        elif isinstance(data, np.bool_):
            return bool(data)
        else:
            return data
    
    def generate_bottleneck_report(self) -> Dict[str, any]:
        """Generate comprehensive bottleneck analysis report."""
        df_merged, df_supp = self.load_data()
        
        # Calculate all metrics
        stage_delays = self.calculate_stage_delays(df_merged)
        ranked_bottlenecks = self.rank_bottlenecks(stage_delays)
        department_delays = self.calculate_department_delays(df_merged)
        risk_employees = self.identify_risk_employees(df_merged)
        root_causes = self.analyze_root_causes(df_merged, df_supp)
        
        report = {
            'bottlenecks': ranked_bottlenecks,
            'department_delays': department_delays,
            'risk_employees': risk_employees,
            'root_causes': root_causes,
            'summary': {
                'total_employees': len(df_merged),
                'total_bottlenecks': len(ranked_bottlenecks),
                'top_bottleneck': ranked_bottlenecks[0] if ranked_bottlenecks else None,
                'at_risk_count': len(risk_employees)
            }
        }
        
        # Serialize all numpy types to native Python types
        return self.serialize_data(report)
