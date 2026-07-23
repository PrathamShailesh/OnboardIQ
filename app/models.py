from sqlalchemy import Column, Integer, String, Boolean, Float
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, index=True)
    employee_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    department = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    manager = Column(String, nullable=True)
    joining_date = Column(String, nullable=True)
    onboarding_status = Column(String, nullable=True)
    laptop_issued = Column(Boolean, nullable=True, default=False)
    access_granted = Column(Boolean, nullable=True, default=False)
    github_username = Column(String, nullable=True)
    slack_id = Column(String, nullable=True)
    jira_id = Column(String, nullable=True)
    location = Column(String, nullable=True)
    employment_type = Column(String, nullable=True)
    salary = Column(Float, nullable=True)
    experience = Column(Float, nullable=True)
