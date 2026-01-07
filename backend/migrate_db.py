"""
Database migration helper - Run this to update existing database schema
WARNING: This will drop existing tables and recreate them. Backup data first!
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from sqlalchemy import text

def drop_all_tables():
    """Drop all existing tables"""
    print("⚠️  Dropping all existing tables...")
    
    with engine.connect() as conn:
        # Drop tables in correct order to avoid FK constraints
        tables = [
            "loan_repayments",
            "credit_history", 
            "transactions",
            "loans",
            "accounts",
            "users"
        ]
        
        for table in tables:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                conn.commit()
                print(f"   ✓ Dropped {table}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {table}: {e}")

def create_all_tables():
    """Create all tables with updated schema"""
    print("\n📦 Creating tables with new schema...")
    
    # Import all models to register them with Base
    from app.users.models import User
    from app.users.credit_history_models import CreditHistory
    from app.accounts.models import Account
    from app.transactions.models import Transaction
    from app.loans.models import Loan
    from app.loans.repayment_models import LoanRepayment
    from app.auth.otp_models import OTP
    from app.db.base import Base
    
    # Create all tables at once using shared Base
    Base.metadata.create_all(bind=engine)
    print("   ✓ Created all tables with relationships")

def migrate():
    """Main migration function"""
    print("=" * 60)
    print("DATABASE MIGRATION - Banking Application")
    print("=" * 60)
    print("\nThis will:")
    print("1. Drop all existing tables")
    print("2. Create new tables with updated schema")
    print("\n⚠️  WARNING: All existing data will be lost!")
    
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Migration cancelled")
        return
    
    try:
        drop_all_tables()
        create_all_tables()
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\nNew features added:")
        print("  • User profile fields for CIBIL calculation")
        print("  • Account balance tracking")
        print("  • Proper foreign key relationships")
        print("  • Loan repayment tracking")
        print("  • Credit history recording")
        print("  • Enhanced CIBIL score calculation")
        print("\nNext steps:")
        print("  1. Update frontend to handle new fields")
        print("  2. Test loan application with CIBIL calculation")
        print("  3. Test transaction balance updates")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
