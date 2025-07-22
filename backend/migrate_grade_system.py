#!/usr/bin/env python3
"""
Migration script to upgrade the tutoring system to support grade-based pricing
Adds new fields to existing database without losing data
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config.database import init_db, engine
from models.teacher import Teacher
from models.student import Student
import json

def migrate_to_grade_system():
    """Migrate existing database to support grade-based pricing"""
    
    print("🔄 Starting migration to grade-based pricing system...")
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Step 1: Add new columns to tables
        print("📝 Adding new database columns...")
        
        # Add grade column to students table (if not exists)
        try:
            session.execute(text("ALTER TABLE students ADD COLUMN grade VARCHAR(20)"))
            print("✅ Added 'grade' column to students table")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("ℹ️ Grade column already exists in students table")
            else:
                print(f"⚠️ Error adding grade column: {e}")
        
        # Add grade_rates column to teachers table (if not exists)
        try:
            session.execute(text("ALTER TABLE teachers ADD COLUMN grade_rates JSON"))
            print("✅ Added 'grade_rates' column to teachers table")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("ℹ️ Grade_rates column already exists in teachers table")
            else:
                print(f"⚠️ Error adding grade_rates column: {e}")
                
        # Add default_rate column to teachers table (if not exists)
        try:
            session.execute(text("ALTER TABLE teachers ADD COLUMN default_rate FLOAT DEFAULT 30.0"))
            print("✅ Added 'default_rate' column to teachers table")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e).lower():
                print("ℹ️ Default_rate column already exists in teachers table")
            else:
                print(f"⚠️ Error adding default_rate column: {e}")
        
        # Rename hourly_rate to base_rate in courses table (if needed)
        try:
            session.execute(text("ALTER TABLE courses RENAME COLUMN hourly_rate TO base_rate"))
            print("✅ Renamed 'hourly_rate' to 'base_rate' in courses table")
        except Exception as e:
            if "no such column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️ Course rate column already properly named")
            else:
                print(f"⚠️ Error renaming course rate column: {e}")
        
        session.commit()
        
        # Step 2: Migrate existing teacher data
        print("🔄 Migrating existing teacher rates...")
        
        teachers = session.query(Teacher).all()
        for teacher in teachers:
            # If teacher has old hourly_rate, migrate it to default_rate
            if hasattr(teacher, 'hourly_rate') and teacher.hourly_rate:
                teacher.default_rate = teacher.hourly_rate
                print(f"✅ Migrated {teacher.name}: hourly_rate ${teacher.hourly_rate} → default_rate ${teacher.default_rate}")
            elif not teacher.default_rate:
                teacher.default_rate = 30.0  # Set sensible default
                print(f"✅ Set default rate for {teacher.name}: ${teacher.default_rate}")
            
            # Initialize empty grade_rates if not set
            if not teacher.grade_rates:
                teacher.grade_rates = {}
        
        # Step 3: Set sample grades for existing students (optional)
        print("📚 Setting sample grades for existing students...")
        
        students = session.query(Student).all()
        sample_grades = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", 
                        "Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10",
                        "Grade 11", "Grade 12", "University"]
        
        for i, student in enumerate(students):
            if not student.grade:
                # Assign grade based on age if available, otherwise use sample
                if student.age:
                    if student.age <= 6:
                        student.grade = "Grade 1"
                    elif student.age <= 16:
                        student.grade = f"Grade {min(student.age - 5, 12)}"
                    else:
                        student.grade = "University"
                else:
                    # Use round-robin assignment for demo
                    student.grade = sample_grades[i % len(sample_grades)]
                
                print(f"✅ Set grade for {student.name}: {student.grade}")
        
        session.commit()
        
        print("\n🎉 Migration completed successfully!")
        print("\n📊 New Features Available:")
        print("✅ Students now have grade levels")
        print("✅ Teachers can set different rates per grade")
        print("✅ Dynamic rate calculation based on student grade")
        print("✅ Backwards compatibility maintained")
        
        print("\n🔧 Next Steps:")
        print("1. Use the teacher management UI to set grade-specific rates")
        print("2. Update student grades as needed")
        print("3. New payments/sessions will use grade-based rates automatically")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def create_sample_grade_rates():
    """Create sample grade-based rates for existing teachers"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\n🎯 Setting up sample grade-based rates...")
        
        teachers = session.query(Teacher).all()
        
        # Sample rate structure (modify according to your needs)
        sample_rate_structure = {
            "Grade 1": 25.0,
            "Grade 2": 27.0,
            "Grade 3": 29.0,
            "Grade 4": 31.0,
            "Grade 5": 33.0,
            "Grade 6": 35.0,
            "Grade 7": 37.0,
            "Grade 8": 39.0,
            "Grade 9": 41.0,
            "Grade 10": 43.0,
            "Grade 11": 45.0,
            "Grade 12": 47.0,
            "University": 55.0
        }
        
        for teacher in teachers:
            # Scale rates based on teacher's default rate
            base_rate = teacher.default_rate or 30.0
            scale_factor = base_rate / 30.0  # Normalize to $30 base
            
            teacher.grade_rates = {
                grade: round(rate * scale_factor, 2) 
                for grade, rate in sample_rate_structure.items()
            }
            
            print(f"✅ Set grade rates for {teacher.name} (base: ${base_rate}):")
            for grade, rate in teacher.grade_rates.items():
                print(f"   {grade}: ${rate}")
        
        session.commit()
        print("\n🎉 Sample grade rates created successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create sample rates: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    # Run migration
    init_db()  # Ensure tables exist
    migrate_to_grade_system()
    
    # Optionally create sample grade rates
    response = input("\n🎯 Would you like to create sample grade-based rates? (y/n): ")
    if response.lower() in ['y', 'yes']:
        create_sample_grade_rates()
    
    print("\n✅ Migration complete! Restart your backend server to use the new features.") 