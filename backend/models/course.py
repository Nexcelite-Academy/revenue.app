from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, unique=True)
    # MODIFIED: Keep base_rate for backwards compatibility, but use teacher's grade-based rates
    base_rate = Column(Float, nullable=False, default=0.0)  # Base rate or fallback rate
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=True)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    
    # Relationships
    teacher = relationship("Teacher", back_populates="courses")
    payments = relationship("Payment", back_populates="course")
    sessions = relationship("Session", back_populates="course")
    
    def get_rate_for_student(self, student):
        """Get appropriate rate for a specific student based on their grade"""
        if self.teacher and student and student.grade:
            # Use teacher's grade-based rate
            return self.teacher.get_rate_for_grade(student.grade)
        elif self.teacher:
            # Use teacher's default rate
            return self.teacher.default_rate
        else:
            # Fallback to course base rate
            return self.base_rate
    
    def get_rate_for_grade(self, grade=None):
        """Get rate for a specific grade"""
        if self.teacher:
            return self.teacher.get_rate_for_grade(grade)
        return self.base_rate
    
    def get_enrollment_count(self):
        """Get number of unique students enrolled in this course"""
        unique_students = set()
        for payment in self.payments:
            unique_students.add(payment.student_id)
        return len(unique_students)
    
    def calculate_total_revenue(self, start_date=None, end_date=None):
        """Calculate total revenue for this course in a date range"""
        payments = self.payments
        if start_date:
            payments = [p for p in payments if p.date >= start_date]
        if end_date:
            payments = [p for p in payments if p.date <= end_date]
        return sum(payment.amount_paid for payment in payments)
    
    def calculate_total_hours_taught(self, start_date=None, end_date=None):
        """Calculate total hours taught for this course"""
        sessions = self.sessions
        if start_date:
            sessions = [s for s in sessions if s.date >= start_date]
        if end_date:
            sessions = [s for s in sessions if s.date <= end_date]
        return sum(session.hours or 0 for session in sessions)
    
    def calculate_salary_cost(self, start_date=None, end_date=None):
        """Calculate total salary cost for this course using grade-based rates"""
        total_cost = 0
        sessions = self.sessions
        if start_date:
            sessions = [s for s in sessions if s.date >= start_date]
        if end_date:
            sessions = [s for s in sessions if s.date <= end_date]
        
        for session in sessions:
            rate = self.get_rate_for_student(session.student) if session.student else self.base_rate
            total_cost += (session.hours or 0) * rate
        
        return total_cost
    
    def get_outstanding_balance(self):
        """Get total outstanding balance (purchased but not used hours) for this course"""
        total_outstanding = 0
        # This would need to be calculated from student balances
        # For now, return 0 - will be implemented in service layer
        return total_outstanding
    
    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', hourly_rate={self.hourly_rate})>" 