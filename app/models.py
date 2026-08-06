from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (UniqueConstraint('employee_id', 'user_id', name='_employee_user_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
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
    # Additional onboarding milestone fields
    training_completed = Column(Boolean, nullable=True, default=False)
    email_setup = Column(Boolean, nullable=True, default=False)
    onboarding_complete = Column(Boolean, nullable=True, default=False)
    # Tool engagement fields
    slack_messages = Column(Integer, nullable=True, default=0)
    github_commits = Column(Integer, nullable=True, default=0)
    jira_tickets_resolved = Column(Integer, nullable=True, default=0)
    slack_reactions = Column(Integer, nullable=True, default=0)
    github_prs_reviewed = Column(Integer, nullable=True, default=0)
    # Timestamps for bottleneck analysis
    laptop_issued_date = Column(String, nullable=True)
    email_setup_date = Column(String, nullable=True)
    access_granted_date = Column(String, nullable=True)
    training_completed_date = Column(String, nullable=True)
    onboarding_complete_date = Column(String, nullable=True)
