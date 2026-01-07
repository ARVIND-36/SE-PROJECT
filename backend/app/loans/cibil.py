from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.users.models import User
from app.accounts.models import Account
from app.loans.models import Loan
from app.loans.repayment_models import LoanRepayment
from app.users.credit_history_models import CreditHistory

def calculate_cibil(user_id: int, db: Session) -> int:
    """
    Calculate CIBIL score based on multiple factors:
    - Payment history (35%)
    - Credit utilization (30%)
    - Credit history length (15%)
    - Credit mix (10%)
    - Recent credit inquiries (10%)
    """
    
    base_score = 300  # Minimum CIBIL score
    max_score = 900   # Maximum CIBIL score
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return base_score
    
    score = 650  # Starting neutral score
    
    # 1. PAYMENT HISTORY (35% weight - most important)
    payment_score = calculate_payment_history(user_id, db)
    score += int(payment_score * 0.35)
    
    # 2. CREDIT UTILIZATION (30% weight)
    utilization_score = calculate_credit_utilization(user_id, db)
    score += int(utilization_score * 0.30)
    
    # 3. CREDIT HISTORY LENGTH (15% weight)
    history_score = calculate_history_length(user_id, db)
    score += int(history_score * 0.15)
    
    # 4. CREDIT MIX (10% weight)
    mix_score = calculate_credit_mix(user_id, db)
    score += int(mix_score * 0.10)
    
    # 5. RECENT INQUIRIES (10% weight)
    inquiry_score = calculate_inquiry_impact(user_id, db)
    score += int(inquiry_score * 0.10)
    
    # Income factor bonus
    if user.monthly_income and user.monthly_income > 50000:
        score += 20
    elif user.monthly_income and user.monthly_income > 30000:
        score += 10
    
    # Employment status bonus
    if user.employment_status == "EMPLOYED":
        score += 15
    elif user.employment_status == "SELF_EMPLOYED":
        score += 10
    
    # Ensure score is within valid range
    score = max(base_score, min(score, max_score))
    
    return score


def calculate_payment_history(user_id: int, db: Session) -> int:
    """
    Calculate score based on loan repayment history.
    Returns score contribution (0-100)
    """
    repayments = db.query(LoanRepayment).join(Loan).filter(
        Loan.user_id == user_id
    ).all()
    
    if not repayments:
        return 0  # No credit history
    
    total_payments = len(repayments)
    on_time_payments = sum(1 for r in repayments if not r.is_delayed and r.status == "PAID")
    delayed_payments = sum(1 for r in repayments if r.is_delayed)
    defaulted_payments = sum(1 for r in repayments if r.status == "DEFAULTED")
    
    # Calculate payment ratio
    if total_payments > 0:
        on_time_ratio = on_time_payments / total_payments
        score = int(on_time_ratio * 100)
        
        # Heavy penalties for defaults and delays
        score -= (defaulted_payments * 20)
        score -= (delayed_payments * 5)
        
        return max(0, score)
    
    return 0


def calculate_credit_utilization(user_id: int, db: Session) -> int:
    """
    Calculate score based on outstanding loan amounts vs income.
    Returns score contribution (0-100)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.monthly_income or user.monthly_income == 0:
        return 50  # Neutral if no income data
    
    active_loans = db.query(Loan).filter(
        Loan.user_id == user_id,
        Loan.status.in_(["APPROVED", "PENDING"])
    ).all()
    
    if not active_loans:
        return 100  # Perfect score if no active debt
    
    total_outstanding = sum(loan.outstanding_amount for loan in active_loans)
    annual_income = user.monthly_income * 12
    
    # Calculate debt-to-income ratio
    if annual_income > 0:
        utilization_ratio = total_outstanding / annual_income
        
        if utilization_ratio < 0.3:  # Less than 30% debt
            return 100
        elif utilization_ratio < 0.5:  # 30-50% debt
            return 75
        elif utilization_ratio < 0.7:  # 50-70% debt
            return 50
        else:  # Over 70% debt
            return 25
    
    return 50


def calculate_history_length(user_id: int, db: Session) -> int:
    """
    Calculate score based on how long user has had credit accounts.
    Returns score contribution (0-100)
    """
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    
    if not accounts:
        return 0
    
    # Find oldest account
    oldest_account = min(accounts, key=lambda a: a.created_at)
    account_age_days = (datetime.now(timezone.utc) - oldest_account.created_at).days
    
    # Score based on account age
    if account_age_days > 365 * 5:  # Over 5 years
        return 100
    elif account_age_days > 365 * 3:  # 3-5 years
        return 80
    elif account_age_days > 365 * 2:  # 2-3 years
        return 60
    elif account_age_days > 365:  # 1-2 years
        return 40
    else:  # Less than 1 year
        return 20


def calculate_credit_mix(user_id: int, db: Session) -> int:
    """
    Calculate score based on variety of credit types.
    Returns score contribution (0-100)
    """
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    
    score = 0
    
    # Having different account types is good
    account_types = set(acc.account_type for acc in accounts)
    score += len(account_types) * 25  # 25 points per account type
    
    # Having loan history is good
    if loans:
        score += 50
    
    return min(100, score)


def calculate_inquiry_impact(user_id: int, db: Session) -> int:
    """
    Calculate score based on recent credit inquiries.
    Returns score contribution (0-100)
    """
    six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)
    
    recent_inquiries = db.query(CreditHistory).filter(
        CreditHistory.user_id == user_id,
        CreditHistory.event_type == "LOAN_APPLIED",
        CreditHistory.event_date >= six_months_ago
    ).count()
    
    # Multiple inquiries in short period is negative
    if recent_inquiries == 0:
        return 100
    elif recent_inquiries == 1:
        return 90
    elif recent_inquiries == 2:
        return 70
    elif recent_inquiries == 3:
        return 50
    else:  # 4 or more
        return 30
