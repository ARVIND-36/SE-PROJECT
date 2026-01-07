from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.auth.dependencies import get_current_user
from .models import Loan
from .cibil import calculate_cibil
from app.users.credit_history_models import CreditHistory
from datetime import datetime, timezone

router = APIRouter(prefix="/loans", tags=["Loans"])

class LoanRequest(BaseModel):
    amount: float
    loan_term_months: int  # Duration in months

@router.post("/apply")
def apply_loan(data: LoanRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Apply for a loan with CIBIL calculation"""
    user_id = current_user["user_id"]
    
    # Calculate CIBIL score
    cibil = calculate_cibil(user_id, db)
    
    # Record credit inquiry
    inquiry = CreditHistory(
        user_id=user_id,
        event_type="LOAN_APPLIED",
        description=f"Loan application for ${data.amount}",
        impact_score=-5,
        inquiry_type="HARD"
    )
    db.add(inquiry)
    
    if cibil < 600:
        db.commit()
        raise HTTPException(status_code=400, detail=f"Low CIBIL score: {cibil}. Minimum required: 600")
    
    # Determine interest rate based on CIBIL
    if cibil >= 750:
        interest = 8.5
    elif cibil >= 700:
        interest = 10.0
    elif cibil >= 650:
        interest = 12.0
    else:
        interest = 14.0
    
    # Calculate monthly EMI
    monthly_rate = interest / 100 / 12
    monthly_emi = data.amount * monthly_rate * (1 + monthly_rate) ** data.loan_term_months / ((1 + monthly_rate) ** data.loan_term_months - 1)
    
    loan = Loan(
        user_id=user_id,
        amount=data.amount,
        interest_rate=interest,
        loan_term_months=data.loan_term_months,
        monthly_emi=round(monthly_emi, 2),
        outstanding_amount=data.amount,
        cibil_score=cibil,
        status="APPROVED",
        approved_at=datetime.now(timezone.utc)
    )
    
    db.add(loan)
    
    # Record loan approval
    approval = CreditHistory(
        user_id=user_id,
        event_type="LOAN_APPROVED",
        description=f"Loan approved for ${data.amount}",
        impact_score=10,
        related_loan_id=loan.id
    )
    db.add(approval)
    
    db.commit()
    
    return {
        "message": "Loan approved",
        "loan_id": loan.id,
        "amount": data.amount,
        "interest_rate": interest,
        "monthly_emi": round(monthly_emi, 2),
        "loan_term_months": data.loan_term_months,
        "cibil_score": cibil
    }

@router.get("/my-loans")
def get_my_loans(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all loans for authenticated user"""
    loans = db.query(Loan).filter(Loan.user_id == current_user["user_id"]).all()
    return loans

@router.get("/cibil-score")
def get_cibil_score(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current CIBIL score for authenticated user"""
    cibil = calculate_cibil(current_user["user_id"], db)
    return {"user_id": current_user["user_id"], "cibil_score": cibil}

