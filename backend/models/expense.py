from sqlalchemy import Column, Integer, String, Float, Date
from datetime import datetime, date
from config.database import Base

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=date.today, index=True)
    item = Column(String(200), nullable=False, index=True)
    amount = Column(Float, nullable=False, default=0.0)
    category = Column(String(50), nullable=True, default='General')
    description = Column(String(500), nullable=True)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    
    def validate_expense(self):
        """Validate expense data"""
        errors = []
        
        if not self.item or len(self.item.strip()) == 0:
            errors.append("Item description is required")
        
        if self.amount <= 0:
            errors.append("Amount must be positive")
        
        if len(self.item) > 200:
            errors.append("Item description too long (max 200 characters)")
        
        if self.description and len(self.description) > 500:
            errors.append("Description too long (max 500 characters)")
        
        return errors
    
    @property
    def formatted_amount(self):
        """Get formatted amount as currency string"""
        return f"${self.amount:.2f}"
    
    def __repr__(self):
        return f"<Expense(id={self.id}, item='{self.item}', amount={self.amount})>" 