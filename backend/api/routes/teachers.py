from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from datetime import datetime, date
from config.database import engine
from models.teacher import Teacher

# Create database session
Session = sessionmaker(bind=engine)

bp = Blueprint('teachers', __name__)

def teacher_to_dict(teacher):
    """Convert Teacher object to dictionary"""
    return {
        'id': teacher.id,
        'name': teacher.name,
        'default_rate': teacher.default_rate,
        'grade_rates': teacher.grade_rates or {},
        'all_rates': teacher.get_all_grades_rates(),
        'created_at': teacher.created_at,
        'updated_at': teacher.updated_at
    }

@bp.route('/', methods=['GET'])
def get_teachers():
    """Get all teachers or search by name"""
    session = Session()
    try:
        search = request.args.get('search', '').strip()
        
        if search:
            teachers = session.query(Teacher).filter(
                Teacher.name.ilike(f'%{search}%')
            ).all()
        else:
            teachers = session.query(Teacher).all()
        
        return jsonify([teacher_to_dict(teacher) for teacher in teachers])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:teacher_id>/', methods=['GET'])
def get_teacher(teacher_id):
    """Get a specific teacher by ID"""
    session = Session()
    try:
        teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        return jsonify(teacher_to_dict(teacher))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/', methods=['POST'])
def create_teacher():
    """Create a new teacher"""
    session = Session()
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Teacher name is required'}), 400
        
        # Check if teacher with same name already exists
        existing = session.query(Teacher).filter(Teacher.name == data['name']).first()
        if existing:
            return jsonify({'error': 'Teacher with this name already exists'}), 400
        
        teacher = Teacher(
            name=data['name'],
            default_rate=float(data.get('default_rate', 30.0)),
            grade_rates=data.get('grade_rates', {})
        )
        
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        
        return jsonify(teacher_to_dict(teacher)), 201
    
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:teacher_id>/', methods=['PUT'])
def update_teacher(teacher_id):
    """Update an existing teacher"""
    session = Session()
    try:
        teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'name' in data:
            # Check for duplicate names (excluding current teacher)
            existing = session.query(Teacher).filter(
                Teacher.name == data['name'],
                Teacher.id != teacher_id
            ).first()
            if existing:
                return jsonify({'error': 'Teacher with this name already exists'}), 400
            teacher.name = data['name']
        
        if 'default_rate' in data:
            teacher.default_rate = float(data['default_rate'])
        
        if 'grade_rates' in data:
            teacher.grade_rates = data['grade_rates']
        
        teacher.updated_at = datetime.now().isoformat()
        
        session.commit()
        
        return jsonify(teacher_to_dict(teacher))
    
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:teacher_id>/grade-rate/', methods=['POST'])
def set_grade_rate(teacher_id):
    """Set rate for a specific grade for a teacher"""
    session = Session()
    try:
        teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('grade') or 'rate' not in data:
            return jsonify({'error': 'Grade and rate are required'}), 400
        
        grade = data['grade']
        rate = float(data['rate'])
        
        if rate < 0:
            return jsonify({'error': 'Rate cannot be negative'}), 400
        
        teacher.set_rate_for_grade(grade, rate)
        teacher.updated_at = datetime.now().isoformat()
        
        session.commit()
        
        return jsonify({
            'message': f'Rate for {grade} set to ${rate}',
            'teacher': teacher_to_dict(teacher)
        })
    
    except ValueError as e:
        return jsonify({'error': f'Invalid rate value: {str(e)}'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:teacher_id>/', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Delete a teacher"""
    session = Session()
    try:
        teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Check if teacher has associated courses, payments, or sessions
        if teacher.courses or teacher.payments or teacher.sessions:
            return jsonify({
                'error': 'Cannot delete teacher with associated courses, payments, or sessions'
            }), 400
        
        session.delete(teacher)
        session.commit()
        
        return jsonify({'message': 'Teacher deleted successfully'})
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:teacher_id>/stats/', methods=['GET'])
def get_teacher_stats(teacher_id):
    """Get teacher statistics for a date range"""
    session = Session()
    try:
        teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
        
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Convert string dates to date objects if provided
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        total_hours = teacher.calculate_total_hours(start_date_obj, end_date_obj)
        total_salary = teacher.calculate_salary(start_date_obj, end_date_obj)
        
        return jsonify({
            'teacher_id': teacher.id,
            'teacher_name': teacher.name,
            'total_hours': total_hours,
            'total_salary': total_salary,
            'default_rate': teacher.default_rate,
            'grade_rates': teacher.grade_rates or {},
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close() 