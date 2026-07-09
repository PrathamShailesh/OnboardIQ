import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for SQLite connection (default to local file)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./onboardiq.db")

# Create SQLAlchemy engine
# connect_args={"check_same_thread": False} is required only for SQLite
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base model for schema definitions
Base = declarative_base()

# Dependency helper to yield and close the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
