from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, timedelta
import csv
import io
from config.database import engine
from models.payment import Payment
from models.session import Session as SessionModel
from models.expense import Expense
from models.student import Student
from models.teacher import Teacher
from models.course import Course

# Create database session
Session = sessionmaker(bind=engine)

bp = Blueprint('reports', __name__)

@bp.route('/financial', methods=['GET'])
def get_financial_report():
    """Get comprehensive financial report"""
    session = Session()
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = date.today()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        # Revenue (from payments)
        payments_query = session.query(Payment).filter(
            Payment.date >= start_date,
            Payment.date <= end_date
        )
        payments = payments_query.all()
        total_revenue = sum(p.amount_paid for p in payments)
        
        # Expenses
        expenses_query = session.query(Expense).filter(
            Expense.date >= start_date,
            Expense.date <= end_date
        )
        expenses = expenses_query.all()
        total_expenses = sum(e.amount for e in expenses)
        
        # Salary costs (from sessions)
        sessions_query = session.query(SessionModel).filter(
            SessionModel.date >= start_date,
            SessionModel.date <= end_date
        )
        sessions = sessions_query.all()
        total_salary_cost = sum(s.salary_cost for s in sessions if s.salary_cost)
        
        # Net profit
        total_costs = total_expenses + total_salary_cost
        net_profit = total_revenue - total_costs
        
        # Course-level analysis
        course_analysis = {}
        for course in session.query(Course).all():
            course_payments = [p for p in payments if p.course_id == course.id]
            course_sessions = [s for s in sessions if s.course_id == course.id]
            
            course_revenue = sum(p.amount_paid for p in course_payments)
            course_salary_cost = sum(s.salary_cost for s in course_sessions if s.salary_cost)
            course_hours_taught = sum(s.hours or 0 for s in course_sessions)
            enrollment_count = len(set(p.student_id for p in course_payments))
            
            # Outstanding balance calculation
            outstanding_balance = 0
            for student in session.query(Student).all():
                outstanding_balance += student.get_balance(course.name)
            
            course_analysis[course.name] = {
                'revenue': course_revenue,
                'salary_cost': course_salary_cost,
                'net_profit': course_revenue - course_salary_cost,
                'hours_taught': course_hours_taught,
                'enrollment_count': enrollment_count,
                'outstanding_balance': outstanding_balance,
                'teacher_name': course.teacher.name if course.teacher else None
            }
        
        # Teacher-level analysis
        teacher_analysis = {}
        for teacher in session.query(Teacher).all():
            teacher_sessions = [s for s in sessions if s.teacher_id == teacher.id]
            teacher_payments = [p for p in payments if p.teacher_id == teacher.id]
            
            total_hours = sum(s.hours or 0 for s in teacher_sessions)
            total_salary = sum(s.salary_cost for s in teacher_sessions if s.salary_cost)
            signed_hours = sum(p.purchased_hours for p in teacher_payments)
            remaining_hours = signed_hours - total_hours
            
            teacher_analysis[teacher.name] = {
                'total_hours': total_hours,
                'total_salary': total_salary,
                'signed_hours': signed_hours,
                'remaining_hours': remaining_hours,
                'sessions_count': len(teacher_sessions),
                'default_rate': teacher.default_rate,
                'grade_rates': teacher.grade_rates or {}
            }
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'total_salary_cost': total_salary_cost,
                'total_costs': total_costs,
                'net_profit': net_profit,
                'profit_margin': (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            },
            'course_analysis': course_analysis,
            'teacher_analysis': teacher_analysis,
            'payment_count': len(payments),
            'session_count': len(sessions),
            'expense_count': len(expenses)
        })
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard summary data"""
    session = Session()
    try:
        # Current month data
        today = date.today()
        start_of_month = today.replace(day=1)
        
        # Revenue this month
        monthly_payments = session.query(Payment).filter(
            Payment.date >= start_of_month,
            Payment.date <= today
        ).all()
        monthly_revenue = sum(p.amount_paid for p in monthly_payments)
        
        # Expenses this month
        monthly_expenses = session.query(Expense).filter(
            Expense.date >= start_of_month,
            Expense.date <= today
        ).all()
        monthly_expense_total = sum(e.amount for e in monthly_expenses)
        
        # Salary costs this month
        monthly_sessions = session.query(SessionModel).filter(
            SessionModel.date >= start_of_month,
            SessionModel.date <= today
        ).all()
        monthly_salary_cost = sum(s.salary_cost for s in monthly_sessions if s.salary_cost)
        
        # Monthly chart data (last 6 months)
        chart_data = []
        for i in range(5, -1, -1):
            month_date = today.replace(day=1) - timedelta(days=i * 30)
            month_start = month_date.replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            
            month_payments = session.query(Payment).filter(
                Payment.date >= month_start,
                Payment.date <= month_end
            ).all()
            
            month_sessions = session.query(SessionModel).filter(
                SessionModel.date >= month_start,
                SessionModel.date <= month_end
            ).all()
            
            month_expenses = session.query(Expense).filter(
                Expense.date >= month_start,
                Expense.date <= month_end
            ).all()
            
            month_revenue = sum(p.amount_paid for p in month_payments)
            month_salary = sum(s.salary_cost for s in month_sessions if s.salary_cost)
            month_other_expenses = sum(e.amount for e in month_expenses)
            month_total_costs = month_salary + month_other_expenses
            
            chart_data.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': month_revenue,
                'costs': month_total_costs,
                'salary': month_salary,
                'expenses': month_other_expenses,
                'profit': month_revenue - month_total_costs
            })
        
        # Low balance alerts
        low_balance_students = []
        for student in session.query(Student).all():
            if student.balances:
                for course_name, balance in student.balances.items():
                    if balance < 2.0:  # threshold for low balance
                        low_balance_students.append({
                            'student_id': student.id,
                            'student_name': student.name,
                            'course_name': course_name,
                            'balance': balance
                        })
        
        # Totals
        total_students = session.query(Student).count()
        total_teachers = session.query(Teacher).count()
        total_courses = session.query(Course).count()
        
        return jsonify({
            'current_month': {
                'revenue': monthly_revenue,
                'expenses': monthly_expense_total,
                'salary_cost': monthly_salary_cost,
                'net_profit': monthly_revenue - monthly_expense_total - monthly_salary_cost
            },
            'chart_data': chart_data,
            'low_balance_alerts': low_balance_students,
            'totals': {
                'students': total_students,
                'teachers': total_teachers,
                'courses': total_courses
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/export/csv', methods=['GET'])
def export_financial_csv():
    """Export financial report as CSV"""
    session = Session()
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400
        
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get financial report data
        payments = session.query(Payment).filter(
            Payment.date >= start_date_obj,
            Payment.date <= end_date_obj
        ).all()
        
        sessions = session.query(SessionModel).filter(
            SessionModel.date >= start_date_obj,
            SessionModel.date <= end_date_obj
        ).all()
        
        expenses = session.query(Expense).filter(
            Expense.date >= start_date_obj,
            Expense.date <= end_date_obj
        ).all()
        
        # Create CSV content
        output = io.StringIO()
        
        # Summary section
        output.write(f"Financial Report Summary\n")
        output.write(f"Period: {start_date} to {end_date}\n\n")
        
        total_revenue = sum(p.amount_paid for p in payments)
        total_salary = sum(s.salary_cost for s in sessions if s.salary_cost)
        total_other_expenses = sum(e.amount for e in expenses)
        net_profit = total_revenue - total_salary - total_other_expenses
        
        output.write(f"Total Revenue,${total_revenue:.2f}\n")
        output.write(f"Total Salary Cost,${total_salary:.2f}\n")
        output.write(f"Total Other Expenses,${total_other_expenses:.2f}\n")
        output.write(f"Net Profit,${net_profit:.2f}\n\n")
        
        # Course analysis
        output.write("Course Analysis\n")
        output.write("Course,Enrollment,Revenue,Salary Cost,Hours Taught,Outstanding Balance\n")
        
        for course in session.query(Course).all():
            course_payments = [p for p in payments if p.course_id == course.id]
            course_sessions = [s for s in sessions if s.course_id == course.id]
            
            enrollment = len(set(p.student_id for p in course_payments))
            revenue = sum(p.amount_paid for p in course_payments)
            salary_cost = sum(s.salary_cost for s in course_sessions if s.salary_cost)
            hours_taught = sum(s.hours or 0 for s in course_sessions)
            
            # Calculate outstanding balance
            outstanding = 0
            for student in session.query(Student).all():
                outstanding += student.get_balance(course.name)
            
            output.write(f"{course.name},{enrollment},${revenue:.2f},${salary_cost:.2f},{hours_taught:.1f},{outstanding:.1f}\n")
        
        output.write("\n")
        
        # Teacher analysis
        output.write("Teacher Analysis\n")
        output.write("Teacher,Hours Taught,Salary Earned,Sessions Count\n")
        
        for teacher in session.query(Teacher).all():
            teacher_sessions = [s for s in sessions if s.teacher_id == teacher.id]
            hours = sum(s.hours or 0 for s in teacher_sessions)
            salary = sum(s.salary_cost for s in teacher_sessions if s.salary_cost)
            sessions_count = len(teacher_sessions)
            
            output.write(f"{teacher.name},{hours:.1f},${salary:.2f},{sessions_count}\n")
        
        # Create response
        csv_content = output.getvalue()
        output.close()
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=financial_report_{start_date}_to_{end_date}.csv'
        
        return response
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/attendance', methods=['GET'])
def get_attendance_report():
    """Get teacher attendance and salary report"""
    session = Session()
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = date.today()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        # Get sessions in date range
        sessions = session.query(SessionModel).filter(
            SessionModel.date >= start_date,
            SessionModel.date <= end_date
        ).all()
        
        # Group by teacher
        teacher_data = {}
        for session_obj in sessions:
            teacher_id = session_obj.teacher_id
            if teacher_id not in teacher_data:
                teacher = session_obj.teacher
                teacher_data[teacher_id] = {
                    'teacher_name': teacher.name if teacher else 'Unknown',
                    'default_rate': teacher.default_rate if teacher else 0,
                    'grade_rates': teacher.grade_rates if teacher else {},
                    'total_hours': 0,
                    'total_salary': 0,
                    'sessions_count': 0,
                    'courses': set()
                }
            
            teacher_data[teacher_id]['total_hours'] += session_obj.hours or 0
            teacher_data[teacher_id]['total_salary'] += session_obj.salary_cost or 0
            teacher_data[teacher_id]['sessions_count'] += 1
            if session_obj.course:
                teacher_data[teacher_id]['courses'].add(session_obj.course.name)
        
        # Convert sets to lists for JSON serialization
        for teacher_id in teacher_data:
            teacher_data[teacher_id]['courses'] = list(teacher_data[teacher_id]['courses'])
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'teachers': list(teacher_data.values()),
            'total_hours': sum(data['total_hours'] for data in teacher_data.values()),
            'total_salary': sum(data['total_salary'] for data in teacher_data.values())
        })
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close() 