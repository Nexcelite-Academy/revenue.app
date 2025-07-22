from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from config.database import Base

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=date.today, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False, index=True)
    hourly_rate = Column(Float, nullable=False)
    purchased_hours = Column(Float, nullable=False, default=0.0)
    discounted_tuition = Column(Float, nullable=False, default=0.0)
    amount_paid = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String(50), nullable=False, default='Cash')
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    
    # Relationships
    student = relationship("Student", back_populates="payments")
    course = relationship("Course", back_populates="payments")
    teacher = relationship("Teacher", back_populates="payments")
    
    @property
    def expected_amount(self):
        """Calculate expected amount based on hours and rate"""
        return self.purchased_hours * self.hourly_rate - self.discounted_tuition
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.expected_amount + self.discounted_tuition > 0:
            return (self.discounted_tuition / (self.expected_amount + self.discounted_tuition)) * 100
        return 0
    
    @property
    def is_overpaid(self):
        """Check if payment amount exceeds expected amount"""
        return self.amount_paid > self.expected_amount
    
    @property
    def is_underpaid(self):
        """Check if payment amount is less than expected amount"""
        return self.amount_paid < self.expected_amount
    
    def validate_payment(self):
        """Validate payment data"""
        errors = []
        
        if self.purchased_hours <= 0:
            errors.append("Purchased hours must be positive")
        
        if self.hourly_rate <= 0:
            errors.append("Hourly rate must be positive")
        
        if self.amount_paid < 0:
            errors.append("Amount paid cannot be negative")
        
        if self.discounted_tuition < 0:
            errors.append("Discount cannot be negative")
        
        if self.discounted_tuition > (self.purchased_hours * self.hourly_rate):
            errors.append("Discount cannot exceed total tuition")
        
        return errors
    
    def __repr__(self):
        return f"<Payment(id={self.id}, student_id={self.student_id}, course_id={self.course_id}, amount={self.amount_paid})>" 