from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from datetime import datetime, date
from config.database import engine
from models.student import Student

# Create database session
Session = sessionmaker(bind=engine)

bp = Blueprint('students', __name__)

def student_to_dict(student):
    """Convert Student object to dictionary"""
    return {
        'id': student.id,
        'name': student.name,
        'gender': student.gender,
        'birthdate': student.birthdate.isoformat() if student.birthdate else None,
        'age': student.age,
        'grade': student.grade,  # NEW: Include grade information
        'parent': student.parent,
        'contact': student.contact,
        'balances': student.balances or {},
        'created_at': student.created_at,
        'updated_at': student.updated_at
    }

@bp.route('/', methods=['GET'])
def get_students():
    """Get all students or search by name"""
    session = Session()
    try:
        search = request.args.get('search', '').strip()
        grade_filter = request.args.get('grade', '').strip()
        
        query = session.query(Student)
        
        if search:
            query = query.filter(
                or_(
                    Student.name.ilike(f'%{search}%'),
                    Student.parent.ilike(f'%{search}%')
                )
            )
        
        if grade_filter:
            query = query.filter(Student.grade == grade_filter)
        
        students = query.all()
        
        return jsonify([student_to_dict(student) for student in students])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:student_id>/', methods=['GET'])
def get_student(student_id):
    """Get a specific student by ID"""
    session = Session()
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        return jsonify(student_to_dict(student))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/', methods=['POST'])
def create_student():
    """Create a new student"""
    session = Session()
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Student name is required'}), 400
        
        if not data.get('gender') or data['gender'] not in ['M', 'F']:
            return jsonify({'error': 'Valid gender (M/F) is required'}), 400
        
        if not data.get('birthdate'):
            return jsonify({'error': 'Birthdate is required'}), 400
        
        # Parse birthdate
        try:
            birthdate = datetime.strptime(data['birthdate'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid birthdate format. Use YYYY-MM-DD'}), 400
        
        student = Student(
            name=data['name'],
            gender=data['gender'],
            birthdate=birthdate,
            grade=data.get('grade'),  # NEW: Include grade
            parent=data.get('parent'),
            contact=data.get('contact'),
            balances=data.get('balances', {})
        )
        
        session.add(student)
        session.commit()
        session.refresh(student)
        
        return jsonify(student_to_dict(student)), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:student_id>/', methods=['PUT'])
def update_student(student_id):
    """Update an existing student"""
    session = Session()
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'name' in data:
            student.name = data['name']
        
        if 'gender' in data:
            if data['gender'] not in ['M', 'F']:
                return jsonify({'error': 'Valid gender (M/F) is required'}), 400
            student.gender = data['gender']
        
        if 'birthdate' in data:
            try:
                student.birthdate = datetime.strptime(data['birthdate'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid birthdate format. Use YYYY-MM-DD'}), 400
        
        if 'grade' in data:  # NEW: Allow grade updates
            student.grade = data['grade']
        
        if 'parent' in data:
            student.parent = data['parent']
        
        if 'contact' in data:
            student.contact = data['contact']
        
        if 'balances' in data:
            student.balances = data['balances']
        
        student.updated_at = datetime.now().isoformat()
        
        session.commit()
        
        return jsonify(student_to_dict(student))
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:student_id>/', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    session = Session()
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        session.delete(student)
        session.commit()
        
        return jsonify({'message': 'Student deleted successfully'})
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:student_id>/balance/<path:course_name>/', methods=['GET'])
def get_student_balance(student_id, course_name):
    """Get student balance for a specific course"""
    session = Session()
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        balance = student.get_balance(course_name)
        
        return jsonify({
            'student_id': student_id,
            'student_name': student.name,
            'student_grade': student.grade,  # NEW: Include grade info
            'course_name': course_name,
            'balance': balance,
            'is_low_balance': student.has_low_balance(course_name)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:student_id>/balance/<path:course_name>/', methods=['PUT'])
def update_student_balance(student_id, course_name):
    """Update student balance for a specific course"""
    session = Session()
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        if not data or 'hours_change' not in data:
            return jsonify({'error': 'hours_change is required'}), 400
        
        hours_change = float(data['hours_change'])
        old_balance = student.get_balance(course_name)
        
        student.update_balance(course_name, hours_change)
        student.updated_at = datetime.now().isoformat()
        
        session.commit()
        
        new_balance = student.get_balance(course_name)
        
        return jsonify({
            'student_id': student_id,
            'student_name': student.name,
            'student_grade': student.grade,  # NEW: Include grade info
            'course_name': course_name,
            'old_balance': old_balance,
            'hours_change': hours_change,
            'new_balance': new_balance,
            'is_low_balance': student.has_low_balance(course_name)
        })
    
    except ValueError as e:
        return jsonify({'error': f'Invalid hours_change value: {str(e)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/grades/', methods=['GET'])
def get_available_grades():
    """Get list of all grades used by students"""
    session = Session()
    try:
        grades = session.query(Student.grade).filter(Student.grade.isnot(None)).distinct().all()
        
        grade_list = [grade[0] for grade in grades if grade[0]]
        
        # Add common grades that might not be in use yet
        common_grades = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6", 
                        "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12", 
                        "University", "Adult Education"]
        
        all_grades = list(set(grade_list + common_grades))
        all_grades.sort()
        
        return jsonify(all_grades)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close() 