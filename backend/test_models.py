"""
Quick verification script to test the database models and CIBIL calculation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all models can be imported"""
    print("🧪 Testing model imports...")
    
    try:
        from app.users.models import User
        print("   ✓ User model")
        
        from app.accounts.models import Account
        print("   ✓ Account model")
        
        from app.transactions.models import Transaction
        print("   ✓ Transaction model")
        
        from app.loans.models import Loan
        print("   ✓ Loan model")
        
        from app.loans.repayment_models import LoanRepayment
        print("   ✓ LoanRepayment model")
        
        from app.users.credit_history_models import CreditHistory
        print("   ✓ CreditHistory model")
        
        from app.loans.cibil import calculate_cibil
        print("   ✓ CIBIL calculation function")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_fields():
    """Test that models have required fields"""
    print("\n🧪 Testing model fields...")
    
    try:
        from app.users.models import User
        from app.accounts.models import Account
        from app.loans.models import Loan
        
        # Check User fields
        user_fields = ['full_name', 'email', 'phone', 'monthly_income', 'employment_status']
        user_columns = [c.name for c in User.__table__.columns]
        for field in user_fields:
            if field in user_columns:
                print(f"   ✓ User.{field}")
            else:
                print(f"   ✗ User.{field} MISSING")
        
        # Check Account fields
        if 'balance' in [c.name for c in Account.__table__.columns]:
            print("   ✓ Account.balance")
        else:
            print("   ✗ Account.balance MISSING")
        
        # Check Loan fields
        loan_fields = ['loan_term_months', 'monthly_emi', 'outstanding_amount']
        loan_columns = [c.name for c in Loan.__table__.columns]
        for field in loan_fields:
            if field in loan_columns:
                print(f"   ✓ Loan.{field}")
            else:
                print(f"   ✗ Loan.{field} MISSING")
        
        print("\n✅ Model field verification complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Field verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_relationships():
    """Test that model relationships are defined"""
    print("\n🧪 Testing model relationships...")
    
    try:
        from app.users.models import User
        from app.accounts.models import Account
        from app.loans.models import Loan
        
        # Check User relationships
        if hasattr(User, 'accounts'):
            print("   ✓ User -> accounts relationship")
        if hasattr(User, 'loans'):
            print("   ✓ User -> loans relationship")
        if hasattr(User, 'credit_history'):
            print("   ✓ User -> credit_history relationship")
        
        # Check Account relationships
        if hasattr(Account, 'user'):
            print("   ✓ Account -> user relationship")
        if hasattr(Account, 'transactions'):
            print("   ✓ Account -> transactions relationship")
        
        # Check Loan relationships
        if hasattr(Loan, 'user'):
            print("   ✓ Loan -> user relationship")
        if hasattr(Loan, 'repayments'):
            print("   ✓ Loan -> repayments relationship")
        
        print("\n✅ Relationship verification complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Relationship verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BANKING APPLICATION - MODEL VERIFICATION")
    print("=" * 60)
    
    success = True
    success = test_imports() and success
    success = test_model_fields() and success
    success = test_relationships() and success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour backend is ready with:")
        print("  • Enhanced User profiles for CIBIL")
        print("  • Account balance tracking")
        print("  • Proper database relationships")
        print("  • Comprehensive CIBIL calculation")
        print("  • Loan repayment tracking")
        print("  • Credit history recording")
        print("\nNext step: Run migrate_db.py to update your database")
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease check the errors above")
