"""
Database initialization file that imports all models to ensure proper table creation
with all relationships. Import this module to initialize the database.
"""

from app.db.database import engine
from sqlalchemy.orm import declarative_base

# Import all models to ensure tables are created in the correct order
from app.users.models import User
from app.users.credit_history_models import CreditHistory
from app.accounts.models import Account
from app.transactions.models import Transaction
from app.loans.models import Loan
from app.loans.repayment_models import LoanRepayment

# Create a unified base
Base = declarative_base()

def init_db():
    """Initialize database tables with all models"""
    # Import all models first
    from app.users.models import Base as UserBase
    from app.accounts.models import Base as AccountBase
    from app.transactions.models import Base as TransactionBase
    from app.loans.models import Base as LoanBase
    from app.loans.repayment_models import Base as RepaymentBase
    from app.users.credit_history_models import Base as CreditBase
    
    # Create all tables
    UserBase.metadata.create_all(bind=engine)
    AccountBase.metadata.create_all(bind=engine)
    TransactionBase.metadata.create_all(bind=engine)
    LoanBase.metadata.create_all(bind=engine)
    RepaymentBase.metadata.create_all(bind=engine)
    CreditBase.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully")

if __name__ == "__main__":
    init_db()
