from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from config.database import engine
from models.payment import Payment
from models.student import Student
from models.course import Course
from models.teacher import Teacher

# Create database session
Session = sessionmaker(bind=engine)

bp = Blueprint('payments', __name__)

def payment_to_dict(payment):
    """Convert Payment object to dictionary"""
    return {
        'id': payment.id,
        'date': payment.date.isoformat() if payment.date else None,
        'student_id': payment.student_id,
        'student_name': payment.student.name if payment.student else None,
        'course_id': payment.course_id,
        'course_name': payment.course.name if payment.course else None,
        'teacher_id': payment.teacher_id,
        'teacher_name': payment.teacher.name if payment.teacher else None,
        'hourly_rate': payment.hourly_rate,
        'purchased_hours': payment.purchased_hours,
        'discounted_tuition': payment.discounted_tuition,
        'amount_paid': payment.amount_paid,
        'payment_method': payment.payment_method,
        'expected_amount': payment.expected_amount,
        'is_overpaid': payment.is_overpaid,
        'is_underpaid': payment.is_underpaid,
        'created_at': payment.created_at,
        'updated_at': payment.updated_at
    }

@bp.route('/', methods=['GET'])
def get_payments():
    """Get all payments with optional filtering"""
    session = Session()
    try:
        # Query parameters for filtering
        student_id = request.args.get('student_id')
        course_id = request.args.get('course_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = session.query(Payment)
        
        if student_id:
            query = query.filter(Payment.student_id == int(student_id))
        
        if course_id:
            query = query.filter(Payment.course_id == int(course_id))
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Payment.date >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Payment.date <= end_date_obj)
        
        payments = query.order_by(Payment.date.desc()).all()
        
        return jsonify([payment_to_dict(payment) for payment in payments])
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Get specific payment by ID"""
    session = Session()
    try:
        payment = session.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify(payment_to_dict(payment))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/', methods=['POST'])
def create_payment():
    """Create new payment and update student balance"""
    session = Session()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['student_id', 'course_id', 'purchased_hours', 'amount_paid']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
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
        payment_date = date.today()
        if data.get('date'):
            try:
                payment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate numeric fields
        try:
            purchased_hours = float(data['purchased_hours'])
            amount_paid = float(data['amount_paid'])
            discounted_tuition = float(data.get('discounted_tuition', 0))
            # Get appropriate rate based on student grade
            if course.teacher and student.grade:
                default_hourly_rate = course.teacher.get_rate_for_grade(student.grade)
            elif course.teacher:
                default_hourly_rate = course.teacher.default_rate
            else:
                default_hourly_rate = course.base_rate
            
            hourly_rate = float(data.get('hourly_rate', default_hourly_rate))
        except (ValueError, TypeError):
            return jsonify({'error': 'Numeric fields must be valid numbers'}), 400
        
        # Create payment
        payment = Payment(
            date=payment_date,
            student_id=student.id,
            course_id=course.id,
            teacher_id=teacher.id,
            hourly_rate=hourly_rate,
            purchased_hours=purchased_hours,
            discounted_tuition=discounted_tuition,
            amount_paid=amount_paid,
            payment_method=data.get('payment_method', 'Cash')
        )
        
        # Validate payment
        validation_errors = payment.validate_payment()
        if validation_errors:
            return jsonify({'error': validation_errors}), 400
        
        # Update student balance
        student.update_balance(course.name, purchased_hours)
        student.updated_at = datetime.now().isoformat()
        
        session.add(payment)
        session.commit()
        session.refresh(payment)
        
        return jsonify(payment_to_dict(payment)), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    """Update existing payment (limited fields)"""
    session = Session()
    try:
        payment = session.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Calculate original balance change to reverse it
        original_hours = payment.purchased_hours
        course = payment.course
        student = payment.student
        
        # Update fields (limited to avoid balance corruption)
        if 'payment_method' in data:
            payment.payment_method = data['payment_method']
        
        if 'amount_paid' in data:
            try:
                payment.amount_paid = float(data['amount_paid'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Amount paid must be a valid number'}), 400
        
        if 'discounted_tuition' in data:
            try:
                payment.discounted_tuition = float(data['discounted_tuition'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Discount must be a valid number'}), 400
        
        # Handle hours change (update balance accordingly)
        if 'purchased_hours' in data:
            try:
                new_hours = float(data['purchased_hours'])
                hours_difference = new_hours - original_hours
                
                # Update payment
                payment.purchased_hours = new_hours
                
                # Update student balance
                student.update_balance(course.name, hours_difference)
                student.updated_at = datetime.now().isoformat()
                
            except (ValueError, TypeError):
                return jsonify({'error': 'Purchased hours must be a valid number'}), 400
        
        # Validate updated payment
        validation_errors = payment.validate_payment()
        if validation_errors:
            return jsonify({'error': validation_errors}), 400
        
        payment.updated_at = datetime.now().isoformat()
        
        session.commit()
        session.refresh(payment)
        
        return jsonify(payment_to_dict(payment))
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    """Delete payment and reverse balance change"""
    session = Session()
    try:
        payment = session.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Reverse the balance change
        student = payment.student
        course = payment.course
        
        # Subtract the purchased hours from balance
        student.update_balance(course.name, -payment.purchased_hours)
        student.updated_at = datetime.now().isoformat()
        
        session.delete(payment)
        session.commit()
        
        return jsonify({'message': 'Payment deleted successfully'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/summary', methods=['GET'])
def get_payment_summary():
    """Get payment summary statistics"""
    session = Session()
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = session.query(Payment)
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Payment.date >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Payment.date <= end_date_obj)
        
        payments = query.all()
        
        total_revenue = sum(p.amount_paid for p in payments)
        total_hours_sold = sum(p.purchased_hours for p in payments)
        total_discounts = sum(p.discounted_tuition for p in payments)
        payment_count = len(payments)
        
        # Payment methods breakdown
        payment_methods = {}
        for payment in payments:
            method = payment.payment_method
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'amount': 0}
            payment_methods[method]['count'] += 1
            payment_methods[method]['amount'] += payment.amount_paid
        
        return jsonify({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_revenue': total_revenue,
                'total_hours_sold': total_hours_sold,
                'total_discounts': total_discounts,
                'payment_count': payment_count,
                'average_payment': total_revenue / payment_count if payment_count > 0 else 0,
                'average_hourly_rate': total_revenue / total_hours_sold if total_hours_sold > 0 else 0
            },
            'payment_methods': payment_methods
        })
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close() 