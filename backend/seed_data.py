#!/usr/bin/env python3
"""
Seed script to populate the database with sample data
"""

from datetime import date, datetime, timedelta
from models import Student, Teacher, Course, Payment, Session as SessionModel, Expense
from config.database import engine, SessionLocal, init_db

def create_sample_data():
    """Create sample data for testing the API"""
    # Initialize database (create tables)
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!")
    
    session = SessionLocal()
    
    try:
        # Clear existing data (only if tables exist)
        try:
            session.query(SessionModel).delete()
            session.query(Payment).delete()
            session.query(Expense).delete()
            session.query(Course).delete()
            session.query(Student).delete()
            session.query(Teacher).delete()
            session.commit()
            print("Cleared existing data.")
        except Exception as e:
            session.rollback()
            print(f"No existing data to clear: {e}")
        
        # Create teachers
        teacher1 = Teacher(name="Alice Johnson", default_rate=30.0)
        teacher2 = Teacher(name="Bob Smith", default_rate=35.0)
        
        session.add(teacher1)
        session.add(teacher2)
        session.commit()
        
        print(f"Created teachers: {teacher1.id}, {teacher2.id}")
        
        # Create courses
        course1 = Course(name="Math Level 1", base_rate=30.0, teacher_id=teacher1.id)
        course2 = Course(name="English Level 1", base_rate=35.0, teacher_id=teacher2.id)
        
        session.add(course1)
        session.add(course2)
        session.commit()
        
        print(f"Created courses: {course1.id}, {course2.id}")
        
        # Create students
        student1 = Student(
            name="Charlie Brown",
            gender="M",
            birthdate=date(2010, 3, 15),
            parent="Lucy Brown",
            contact="charlie@example.com",
            balances={"Math Level 1": 5.0}
        )
        
        student2 = Student(
            name="Daisy Miller",
            gender="F",
            birthdate=date(2009, 8, 22),
            parent="Ann Miller",
            contact="daisy@example.com",
            balances={"English Level 1": 3.0}
        )
        
        session.add(student1)
        session.add(student2)
        session.commit()
        
        print(f"Created students: {student1.id}, {student2.id}")
        
        # Create payment
        payment1 = Payment(
            date=date.today(),
            student_id=student1.id,
            course_id=course1.id,
            teacher_id=teacher1.id,
            hourly_rate=30.0,
            purchased_hours=5.0,
            discounted_tuition=0.0,
            amount_paid=150.0,
            payment_method="Cash"
        )
        
        session.add(payment1)
        session.commit()
        
        print(f"Created payment: {payment1.id}")
        
        # Create session
        session_obj = SessionModel(
            date=date.today(),
            student_id=student1.id,
            course_id=course1.id,
            teacher_id=teacher1.id,
            start_time="10:00",
            end_time="11:30",
            notes="Regular math session"
        )
        session_obj.calculate_hours()
        
        # Update student balance (deduct session hours)
        student1.update_balance("Math Level 1", -session_obj.hours)
        
        session.add(session_obj)
        session.commit()
        
        print(f"Created session: {session_obj.id}, hours: {session_obj.hours}")
        
        # Create expense
        expense1 = Expense(
            date=date.today(),
            item="Office supplies",
            amount=25.50,
            category="Office",
            description="Pens, paper, and notebooks"
        )
        
        session.add(expense1)
        session.commit()
        
        print(f"Created expense: {expense1.id}")
        
        print("\nSample data created successfully!")
        print(f"Students: {session.query(Student).count()}")
        print(f"Teachers: {session.query(Teacher).count()}")
        print(f"Courses: {session.query(Course).count()}")
        print(f"Payments: {session.query(Payment).count()}")
        print(f"Sessions: {session.query(SessionModel).count()}")
        print(f"Expenses: {session.query(Expense).count()}")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating sample data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_sample_data() 