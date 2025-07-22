from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from config.database import engine
from models.session import Session as SessionModel
from models.student import Student
from models.course import Course
from models.teacher import Teacher

# Create database session
Session = sessionmaker(bind=engine)

bp = Blueprint('sessions', __name__)

def session_to_dict(session_obj):
    """Convert Session object to dictionary"""
    return {
        'id': session_obj.id,
        'date': session_obj.date.isoformat() if session_obj.date else None,
        'student_id': session_obj.student_id,
        'student_name': session_obj.student.name if session_obj.student else None,
        'course_id': session_obj.course_id,
        'course_name': session_obj.course.name if session_obj.course else None,
        'teacher_id': session_obj.teacher_id,
        'teacher_name': session_obj.teacher.name if session_obj.teacher else None,
        'start_time': session_obj.start_time,
        'end_time': session_obj.end_time,
        'hours': session_obj.hours,
        'duration_formatted': session_obj.duration_formatted,
        'salary_cost': session_obj.salary_cost,
        'notes': session_obj.notes,
        'created_at': session_obj.created_at,
        'updated_at': session_obj.updated_at
    }

@bp.route('/', methods=['GET'])
def get_sessions():
    """Get all sessions with optional filtering"""
    session = Session()
    try:
        # Query parameters for filtering
        student_id = request.args.get('student_id')
        course_id = request.args.get('course_id')
        teacher_id = request.args.get('teacher_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = session.query(SessionModel)
        
        if student_id:
            query = query.filter(SessionModel.student_id == int(student_id))
        
        if course_id:
            query = query.filter(SessionModel.course_id == int(course_id))
        
        if teacher_id:
            query = query.filter(SessionModel.teacher_id == int(teacher_id))
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(SessionModel.date >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(SessionModel.date <= end_date_obj)
        
        sessions = query.order_by(SessionModel.date.desc(), SessionModel.start_time.desc()).all()
        
        return jsonify([session_to_dict(s) for s in sessions])
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session by ID"""
    session = Session()
    try:
        session_obj = session.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify(session_to_dict(session_obj))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/', methods=['POST'])
def create_session():
    """Create new session and deduct from student balance"""
    session = Session()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['student_id', 'course_id', 'start_time', 'end_time']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate and get related entities
        student = session.query(Student).filter(Student.id == data['student_id']).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        course = session.query(Course).filter(Course.id == data['course_id']).first()
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Use course's teacher if not specified
        teacher_id = data.get('teacher_id', course.teacher_id)
        if not teacher_id:
            return jsonify({'error': 'No teacher assigned to this course'}), 400
        
        teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Parse date
        session_date = date.today()
        if data.get('date'):
            try:
                session_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Create session
        session_obj = SessionModel(
            date=session_date,
            student_id=student.id,
            course_id=course.id,
            teacher_id=teacher.id,
            start_time=data['start_time'],
            end_time=data['end_time'],
            notes=data.get('notes', '')
        )
        
        # Calculate hours
        calculated_hours = session_obj.calculate_hours()
        
        # Validate session
        validation_errors = session_obj.validate_session()
        if validation_errors:
            return jsonify({'error': validation_errors}), 400
        
        # Check if student has sufficient balance
        current_balance = student.get_balance(course.name)
        if current_balance < calculated_hours:
            return jsonify({
                'error': f'Insufficient balance. Current: {current_balance:.1f}h, Required: {calculated_hours:.1f}h'
            }), 400
        
        # Deduct from student balance
        student.update_balance(course.name, -calculated_hours)
        student.updated_at = datetime.now().isoformat()
        
        session.add(session_obj)
        session.commit()
        session.refresh(session_obj)
        
        return jsonify(session_to_dict(session_obj)), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    """Update existing session"""
    session = Session()
    try:
        session_obj = session.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Store original hours for balance adjustment
        original_hours = session_obj.hours or 0
        course = session_obj.course
        student = session_obj.student
        
        # Update fields
        if 'start_time' in data:
            session_obj.start_time = data['start_time']
        
        if 'end_time' in data:
            session_obj.end_time = data['end_time']
        
        if 'notes' in data:
            session_obj.notes = data.get('notes', '')
        
        if 'date' in data and data['date']:
            try:
                session_obj.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Recalculate hours if time changed
        if 'start_time' in data or 'end_time' in data:
            new_hours = session_obj.calculate_hours()
            hours_difference = new_hours - original_hours
            
            # Check if student has sufficient balance for increase
            if hours_difference > 0:
                current_balance = student.get_balance(course.name)
                if current_balance < hours_difference:
                    return jsonify({
                        'error': f'Insufficient balance for increase. Available: {current_balance:.1f}h, Required: {hours_difference:.1f}h'
                    }), 400
            
            # Update student balance with the difference
            student.update_balance(course.name, -hours_difference)
            student.updated_at = datetime.now().isoformat()
        
        # Validate updated session
        validation_errors = session_obj.validate_session()
        if validation_errors:
            return jsonify({'error': validation_errors}), 400
        
        session_obj.updated_at = datetime.now().isoformat()
        
        session.commit()
        session.refresh(session_obj)
        
        return jsonify(session_to_dict(session_obj))
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session and restore balance"""
    session = Session()
    try:
        session_obj = session.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404
        
        # Restore the balance
        student = session_obj.student
        course = session_obj.course
        hours_to_restore = session_obj.hours or 0
        
        if hours_to_restore > 0:
            student.update_balance(course.name, hours_to_restore)
            student.updated_at = datetime.now().isoformat()
        
        session.delete(session_obj)
        session.commit()
        
        return jsonify({'message': 'Session deleted successfully'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/summary', methods=['GET'])
def get_session_summary():
    """Get session summary statistics"""
    session = Session()
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = session.query(SessionModel)
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(SessionModel.date >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(SessionModel.date <= end_date_obj)
        
        sessions = query.all()
        
        total_hours = sum(s.hours or 0 for s in sessions)
        total_salary_cost = sum(s.salary_cost for s in sessions)
        session_count = len(sessions)
        
        # Teacher breakdown
        teacher_stats = {}
        for s in sessions:
            teacher_name = s.teacher.name if s.teacher else 'Unknown'
            if teacher_name not in teacher_stats:
                teacher_stats[teacher_name] = {
                    'sessions': 0,
                    'hours': 0,
                    'salary_cost': 0
                }
            teacher_stats[teacher_name]['sessions'] += 1
            teacher_stats[teacher_name]['hours'] += s.hours or 0
            teacher_stats[teacher_name]['salary_cost'] += s.salary_cost
        
        # Course breakdown
        course_stats = {}
        for s in sessions:
            course_name = s.course.name if s.course else 'Unknown'
            if course_name not in course_stats:
                course_stats[course_name] = {
                    'sessions': 0,
                    'hours': 0,
                    'salary_cost': 0
                }
            course_stats[course_name]['sessions'] += 1
            course_stats[course_name]['hours'] += s.hours or 0
            course_stats[course_name]['salary_cost'] += s.salary_cost
        
        return jsonify({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_hours': total_hours,
                'total_salary_cost': total_salary_cost,
                'session_count': session_count,
                'average_session_length': total_hours / session_count if session_count > 0 else 0,
                'average_salary_per_hour': total_salary_cost / total_hours if total_hours > 0 else 0
            },
            'teacher_breakdown': teacher_stats,
            'course_breakdown': course_stats
        })
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close() 