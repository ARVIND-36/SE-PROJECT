from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from .models import Loan
from .cibil import calculate_cibil

router = APIRouter(prefix="/loans", tags=["Loans"])

class LoanRequest(BaseModel):
    user_id: int
    amount: float

@router.post("/apply")
def apply_loan(data: LoanRequest, db: Session = Depends(get_db)):
    cibil = calculate_cibil(data.user_id)

    if cibil < 600:
        raise HTTPException(status_code=400, detail="Low CIBIL score")

    interest = 10.0 if cibil >= 700 else 14.0

    loan = Loan(
        user_id=data.user_id,
        amount=data.amount,
        interest_rate=interest,
        cibil_score=cibil,
        status="APPROVED"
    )

    db.add(loan)
    db.commit()

    return {
        "message": "Loan approved",
        "interest_rate": interest,
        "cibil_score": cibil
    }

