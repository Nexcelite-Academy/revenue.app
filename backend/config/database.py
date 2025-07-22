import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tutoring_center.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv('DEBUG') else False,
    connect_args={"check_same_thread": False} if 'sqlite' in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Database dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database - create all tables"""
    print(f"Creating tables with database URL: {DATABASE_URL}")
    
    # Import all models to ensure they're registered with Base
    try:
        # Try relative imports first (for Railway deployment)
        from models.student import Student
        from models.teacher import Teacher
        from models.course import Course
        from models.payment import Payment
        from models.session import Session
        from models.expense import Expense
    except ImportError:
        # Fallback to absolute imports (for local development)
        from backend.models.student import Student
        from backend.models.teacher import Teacher
        from backend.models.course import Course
        from backend.models.payment import Payment
        from backend.models.session import Session
        from backend.models.expense import Expense
    
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!") 