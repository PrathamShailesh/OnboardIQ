import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Database URL configuration
# Supports both SQLite (development) and PostgreSQL (production)
# Set DATABASE_URL environment variable for PostgreSQL, e.g.:
# postgresql://username:password@localhost:5432/onboardiq
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./onboardiq.db")

# Create SQLAlchemy engine
# connect_args={"check_same_thread": False} is required only for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,        # Connection pool size
        max_overflow=20      # Max overflow connections
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
