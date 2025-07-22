from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class Teacher(Base):
    __tablename__ = 'teachers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    # REMOVED: hourly_rate = Column(Float, nullable=False, default=0.0)
    # NEW: Grade-based rate matrix
    grade_rates = Column(JSON, default=dict)  # {"Grade 1": 25.0, "Grade 2": 30.0, "High School": 45.0, "University": 60.0}
    default_rate = Column(Float, nullable=False, default=30.0)  # Fallback rate if grade not specified
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    
    # Relationships
    courses = relationship("Course", back_populates="teacher", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="teacher")
    sessions = relationship("Session", back_populates="teacher")
    
    def get_rate_for_grade(self, grade=None):
        """Get hourly rate for a specific grade"""
        if not grade or not self.grade_rates:
            return self.default_rate
        
        return self.grade_rates.get(grade, self.default_rate)
    
    def set_rate_for_grade(self, grade, rate):
        """Set hourly rate for a specific grade"""
        if not self.grade_rates:
            self.grade_rates = {}
        
        self.grade_rates[grade] = float(rate)
        # SQLAlchemy requires explicit flag for JSON field updates
        self.grade_rates = dict(self.grade_rates)
    
    def get_all_grades_rates(self):
        """Get all grades and their rates"""
        rates = dict(self.grade_rates) if self.grade_rates else {}
        rates['Default'] = self.default_rate
        return rates
    
    def calculate_total_hours(self, start_date=None, end_date=None):
        """Calculate total hours taught in a date range"""
        sessions = self.sessions
        if start_date:
            sessions = [s for s in sessions if s.date >= start_date]
        if end_date:
            sessions = [s for s in sessions if s.date <= end_date]
        return sum(session.hours or 0 for session in sessions)
    
    def calculate_salary(self, start_date=None, end_date=None):
        """Calculate total salary for a date range using grade-based rates"""
        total_salary = 0
        sessions = self.sessions
        if start_date:
            sessions = [s for s in sessions if s.date >= start_date]
        if end_date:
            sessions = [s for s in sessions if s.date <= end_date]
        
        for session in sessions:
            student_grade = session.student.grade if session.student else None
            rate = self.get_rate_for_grade(student_grade)
            total_salary += (session.hours or 0) * rate
        
        return total_salary
    
    def __repr__(self):
        return f"<Teacher(id={self.id}, name='{self.name}', default_rate={self.default_rate})>" 