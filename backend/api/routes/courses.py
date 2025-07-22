from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from datetime import datetime
from config.database import engine
from models.course import Course
from models.teacher import Teacher

# Create database session
Session = sessionmaker(bind=engine)

bp = Blueprint('courses', __name__)

def course_to_dict(course):
    """Convert Course object to dictionary"""
    return {
        'id': course.id,
        'name': course.name,
        'base_rate': course.base_rate,
        'teacher_id': course.teacher_id,
        'teacher_name': course.teacher.name if course.teacher else None,
        'created_at': course.created_at,
        'updated_at': course.updated_at
    }

@bp.route('/', methods=['GET'])
def get_courses():
    """Get all courses or search by name"""
    session = Session()
    try:
        search = request.args.get('search', '').strip()
        
        if search:
            courses = session.query(Course).filter(
                Course.name.ilike(f'%{search}%')
            ).all()
        else:
            courses = session.query(Course).all()
        
        return jsonify([course_to_dict(course) for course in courses])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get specific course by ID"""
    session = Session()
    try:
        course = session.query(Course).filter(Course.id == course_id).first()
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        return jsonify(course_to_dict(course))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/', methods=['POST'])
def create_course():
    """Create new course"""
    session = Session()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'base_rate']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate base rate
        try:
            base_rate = float(data['base_rate'])
            if base_rate <= 0:
                return jsonify({'error': 'Base rate must be positive'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Base rate must be a valid number'}), 400
        
        # Validate teacher if provided
        teacher_id = data.get('teacher_id')
        if teacher_id:
            try:
                teacher_id = int(teacher_id)
                teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
                if not teacher:
                    return jsonify({'error': 'Teacher not found'}), 404
            except (ValueError, TypeError):
                return jsonify({'error': 'Teacher ID must be a valid number'}), 400
        
        # Check for duplicate course name
        existing_course = session.query(Course).filter(Course.name == data['name'].strip()).first()
        if existing_course:
            return jsonify({'error': 'Course name already exists'}), 400
        
        # Create course
        course = Course(
            name=data['name'].strip(),
            base_rate=base_rate,
            teacher_id=teacher_id
        )
        
        session.add(course)
        session.commit()
        session.refresh(course)
        
        return jsonify(course_to_dict(course)), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update existing course"""
    session = Session()
    try:
        course = session.query(Course).filter(Course.id == course_id).first()
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data and data['name']:
            new_name = data['name'].strip()
            # Check for duplicate name (excluding current course)
            existing_course = session.query(Course).filter(
                Course.name == new_name,
                Course.id != course_id
            ).first()
            if existing_course:
                return jsonify({'error': 'Course name already exists'}), 400
            course.name = new_name
        
        if 'base_rate' in data and data['base_rate'] is not None:
            try:
                base_rate = float(data['base_rate'])
                if base_rate <= 0:
                    return jsonify({'error': 'Base rate must be positive'}), 400
                course.base_rate = base_rate
            except (ValueError, TypeError):
                return jsonify({'error': 'Base rate must be a valid number'}), 400
        
        if 'teacher_id' in data:
            teacher_id = data['teacher_id']
            if teacher_id:
                try:
                    teacher_id = int(teacher_id)
                    teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
                    if not teacher:
                        return jsonify({'error': 'Teacher not found'}), 404
                    course.teacher_id = teacher_id
                except (ValueError, TypeError):
                    return jsonify({'error': 'Teacher ID must be a valid number'}), 400
            else:
                course.teacher_id = None
        
        course.updated_at = datetime.now().isoformat()
        
        session.commit()
        session.refresh(course)
        
        return jsonify(course_to_dict(course))
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete course"""
    session = Session()
    try:
        course = session.query(Course).filter(Course.id == course_id).first()
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if course has associated payments or sessions
        if course.payments or course.sessions:
            return jsonify({
                'error': 'Cannot delete course with associated payments or sessions. Please remove them first.'
            }), 400
        
        session.delete(course)
        session.commit()
        
        return jsonify({'message': 'Course deleted successfully'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:course_id>/stats', methods=['GET'])
def get_course_stats(course_id):
    """Get course statistics"""
    session = Session()
    try:
        course = session.query(Course).filter(Course.id == course_id).first()
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Parse dates if provided
        start_date_obj = None
        end_date_obj = None
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        # Calculate stats
        enrollment_count = course.get_enrollment_count()
        total_revenue = course.calculate_total_revenue(start_date_obj, end_date_obj)
        total_hours_taught = course.calculate_total_hours_taught(start_date_obj, end_date_obj)
        
        # Filter sessions by date range if specified
        sessions = course.sessions
        if start_date_obj:
            sessions = [s for s in sessions if s.date >= start_date_obj]
        if end_date_obj:
            sessions = [s for s in sessions if s.date <= end_date_obj]
        
        sessions_count = len(sessions)
        
        # Calculate salary cost
        total_salary_cost = sum(s.salary_cost for s in sessions if s.salary_cost)
        
        return jsonify({
            'course_id': course_id,
            'course_name': course.name,
            'base_rate': course.base_rate,
            'teacher_name': course.teacher.name if course.teacher else None,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'stats': {
                'enrollment_count': enrollment_count,
                'total_revenue': total_revenue,
                'total_hours_taught': total_hours_taught,
                'total_salary_cost': total_salary_cost,
                'sessions_count': sessions_count,
                'net_profit': total_revenue - total_salary_cost,
                'average_session_length': total_hours_taught / sessions_count if sessions_count > 0 else 0
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close() 