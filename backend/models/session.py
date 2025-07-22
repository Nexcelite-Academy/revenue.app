from sqlalchemy import Column, Integer, String, Float, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date, time as time_obj
from config.database import Base

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=date.today, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False, index=True)
    start_time = Column(String(10), nullable=False)  # Store as "HH:MM" format
    end_time = Column(String(10), nullable=False)    # Store as "HH:MM" format
    hours = Column(Float, nullable=True)  # Calculated from start/end time
    notes = Column(String(500), nullable=True)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    
    # Relationships
    student = relationship("Student", back_populates="sessions")
    course = relationship("Course", back_populates="sessions")
    teacher = relationship("Teacher", back_populates="sessions")
    
    def calculate_hours(self):
        """Calculate hours from start and end time"""
        try:
            # Parse time strings (format: "HH:MM")
            start_parts = self.start_time.split(':')
            end_parts = self.end_time.split(':')
            
            start_hour, start_min = int(start_parts[0]), int(start_parts[1])
            end_hour, end_min = int(end_parts[0]), int(end_parts[1])
            
            # Convert to minutes
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            
            # Handle sessions that cross midnight
            if end_minutes < start_minutes:
                end_minutes += 24 * 60
            
            # Calculate difference in hours
            duration_minutes = end_minutes - start_minutes
            duration_hours = duration_minutes / 60.0
            
            self.hours = round(duration_hours, 2)
            return self.hours
            
        except (ValueError, IndexError):
            return 0.0
    
    @property
    def duration_formatted(self):
        """Get formatted duration string"""
        if self.hours:
            hours = int(self.hours)
            minutes = int((self.hours - hours) * 60)
            if hours > 0 and minutes > 0:
                return f"{hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h"
            else:
                return f"{minutes}m"
        return "0m"
    
    @property
    def salary_cost(self):
        """Calculate salary cost for this session using grade-based rates"""
        if self.teacher and self.hours and self.student:
            # Use grade-based rate calculation
            rate = self.teacher.get_rate_for_grade(self.student.grade)
            return self.hours * rate
        elif self.teacher and self.hours:
            # Fallback to default rate if no student info
            return self.hours * self.teacher.default_rate
        return 0.0
    
    def validate_session(self):
        """Validate session data"""
        errors = []
        
        if not self.start_time or not self.end_time:
            errors.append("Start time and end time are required")
            return errors
        
        # Validate time format
        try:
            start_parts = self.start_time.split(':')
            end_parts = self.end_time.split(':')
            
            if len(start_parts) != 2 or len(end_parts) != 2:
                errors.append("Time format must be HH:MM")
                return errors
            
            start_hour, start_min = int(start_parts[0]), int(start_parts[1])
            end_hour, end_min = int(end_parts[0]), int(end_parts[1])
            
            if not (0 <= start_hour <= 23 and 0 <= start_min <= 59):
                errors.append("Invalid start time")
            
            if not (0 <= end_hour <= 23 and 0 <= end_min <= 59):
                errors.append("Invalid end time")
                
        except ValueError:
            errors.append("Time format must be HH:MM with valid numbers")
        
        # Calculate and validate duration
        calculated_hours = self.calculate_hours()
        if calculated_hours <= 0:
            errors.append("End time must be after start time")
        elif calculated_hours > 12:  # Reasonable maximum session length
            errors.append("Session duration cannot exceed 12 hours")
        
        return errors
    
    def can_deduct_balance(self):
        """Check if student has sufficient balance for this session"""
        if self.student and self.course and self.hours:
            current_balance = self.student.get_balance(self.course.name)
            return current_balance >= self.hours
        return False
    
    def __repr__(self):
        return f"<Session(id={self.id}, student_id={self.student_id}, course_id={self.course_id}, hours={self.hours})>" 