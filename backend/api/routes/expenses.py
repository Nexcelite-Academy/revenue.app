from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from config.database import engine
from models.expense import Expense

# Create database session
Session = sessionmaker(bind=engine)

bp = Blueprint('expenses', __name__)

def expense_to_dict(expense):
    """Convert Expense object to dictionary"""
    return {
        'id': expense.id,
        'date': expense.date.isoformat() if expense.date else None,
        'item': expense.item,
        'amount': expense.amount,
        'category': expense.category,
        'description': expense.description,
        'formatted_amount': expense.formatted_amount,
        'created_at': expense.created_at,
        'updated_at': expense.updated_at
    }

@bp.route('/', methods=['GET'])
def get_expenses():
    """Get all expenses with optional filtering"""
    session = Session()
    try:
        # Query parameters for filtering
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search', '').strip()
        
        query = session.query(Expense)
        
        if category:
            query = query.filter(Expense.category == category)
        
        if search:
            query = query.filter(Expense.item.ilike(f'%{search}%'))
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= end_date_obj)
        
        expenses = query.order_by(Expense.date.desc()).all()
        
        return jsonify([expense_to_dict(expense) for expense in expenses])
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """Get specific expense by ID"""
    session = Session()
    try:
        expense = session.query(Expense).filter(Expense.id == expense_id).first()
        
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        return jsonify(expense_to_dict(expense))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/', methods=['POST'])
def create_expense():
    """Create new expense"""
    session = Session()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['item', 'amount']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Parse date
        expense_date = date.today()
        if data.get('date'):
            try:
                expense_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate amount
        try:
            amount = float(data['amount'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Amount must be a valid number'}), 400
        
        # Create expense
        expense = Expense(
            date=expense_date,
            item=data['item'].strip(),
            amount=amount,
            category=data.get('category', 'General').strip(),
            description=data.get('description', '').strip() if data.get('description') else None
        )
        
        # Validate expense
        validation_errors = expense.validate_expense()
        if validation_errors:
            return jsonify({'error': validation_errors}), 400
        
        session.add(expense)
        session.commit()
        session.refresh(expense)
        
        return jsonify(expense_to_dict(expense)), 201
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update existing expense"""
    session = Session()
    try:
        expense = session.query(Expense).filter(Expense.id == expense_id).first()
        
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'item' in data and data['item']:
            expense.item = data['item'].strip()
        
        if 'amount' in data and data['amount'] is not None:
            try:
                expense.amount = float(data['amount'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Amount must be a valid number'}), 400
        
        if 'category' in data:
            expense.category = data['category'].strip() if data['category'] else 'General'
        
        if 'description' in data:
            expense.description = data['description'].strip() if data['description'] else None
        
        if 'date' in data and data['date']:
            try:
                expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate updated expense
        validation_errors = expense.validate_expense()
        if validation_errors:
            return jsonify({'error': validation_errors}), 400
        
        expense.updated_at = datetime.now().isoformat()
        
        session.commit()
        session.refresh(expense)
        
        return jsonify(expense_to_dict(expense))
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete expense"""
    session = Session()
    try:
        expense = session.query(Expense).filter(Expense.id == expense_id).first()
        
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        session.delete(expense)
        session.commit()
        
        return jsonify({'message': 'Expense deleted successfully'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/categories', methods=['GET'])
def get_expense_categories():
    """Get all unique expense categories"""
    session = Session()
    try:
        categories = session.query(Expense.category.distinct()).all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify(sorted(category_list))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@bp.route('/summary', methods=['GET'])
def get_expense_summary():
    """Get expense summary statistics"""
    session = Session()
    try:
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = session.query(Expense)
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= end_date_obj)
        
        expenses = query.all()
        
        total_amount = sum(e.amount for e in expenses)
        expense_count = len(expenses)
        
        # Category breakdown
        category_stats = {}
        for expense in expenses:
            category = expense.category or 'Uncategorized'
            if category not in category_stats:
                category_stats[category] = {'count': 0, 'amount': 0}
            category_stats[category]['count'] += 1
            category_stats[category]['amount'] += expense.amount
        
        # Monthly breakdown (last 12 months)
        monthly_stats = {}
        for expense in expenses:
            month_key = expense.date.strftime('%Y-%m') if expense.date else 'Unknown'
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'count': 0, 'amount': 0}
            monthly_stats[month_key]['count'] += 1
            monthly_stats[month_key]['amount'] += expense.amount
        
        return jsonify({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_amount': total_amount,
                'expense_count': expense_count,
                'average_expense': total_amount / expense_count if expense_count > 0 else 0
            },
            'category_breakdown': category_stats,
            'monthly_breakdown': dict(sorted(monthly_stats.items(), reverse=True))
        })
    
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close() 