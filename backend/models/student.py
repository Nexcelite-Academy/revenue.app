from sqlalchemy import Column, Integer, String, Date, Text, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import date, datetime
from config.database import Base

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    gender = Column(Enum('M', 'F', name='gender_enum'), nullable=False)
    birthdate = Column(Date, nullable=False)
    grade = Column(String(20), nullable=True, index=True)  # NEW: Grade level (e.g., "Grade 1", "Grade 2", "High School", "University")
    parent = Column(String(100), nullable=True)
    contact = Column(String(255), nullable=True)
    balances = Column(JSON, default=dict)  # Store course balances as JSON
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    
    # Relationships
    payments = relationship("Payment", back_populates="student", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="student", cascade="all, delete-orphan")
    
    @property
    def age(self):
        """Calculate age from birthdate"""
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None
    
    def get_balance(self, course_name):
        """Get balance hours for a specific course"""
        return self.balances.get(course_name, 0.0) if self.balances else 0.0
    
    def update_balance(self, course_name, hours_change):
        """Update balance for a specific course"""
        if not self.balances:
            self.balances = {}
        
        current_balance = self.balances.get(course_name, 0.0)
        new_balance = max(0, current_balance + hours_change)  # Prevent negative balances
        self.balances[course_name] = new_balance
        
        # SQLAlchemy requires explicit flag for JSON field updates
        self.balances = dict(self.balances)
        
    def has_low_balance(self, course_name, threshold=2.0):
        """Check if student has low balance for a course"""
        return self.get_balance(course_name) < threshold
    
    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', age={self.age})>" 