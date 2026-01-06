from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from .models import Transaction
from app.accounts.models import Account
from datetime import date
router = APIRouter(prefix="/transactions", tags=["Transactions"])

class TransferRequest(BaseModel):
    from_account: int
    to_account: int
    amount: float

def get_balance(account_id: int, db: Session):
    credits = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.type == "CREDIT"
    ).all()

    debits = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.type == "DEBIT"
    ).all()

    return sum(c.amount for c in credits) - sum(d.amount for d in debits)

DAILY_LIMIT = 25000

def today_debit_total(account_id: int, db: Session):
    today = date.today()
    debits = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.type == "DEBIT",
        Transaction.created_at >= today
    ).all()
    return sum(d.amount for d in debits)

@router.post("/transfer")
def transfer(data: TransferRequest, db: Session = Depends(get_db)):
    # Check if sender account is frozen
    sender = db.query(Account).filter(Account.id == data.from_account).first()
    if sender.status == "FROZEN":
        raise HTTPException(status_code=403, detail="Account is frozen")
    
    # Check daily withdrawal limit
    today_total = today_debit_total(data.from_account, db)
    if today_total + data.amount > DAILY_LIMIT:
        raise HTTPException(status_code=400, detail="Daily withdrawal limit exceeded")
    
    sender_balance = get_balance(data.from_account, db)

    if sender_balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    debit = Transaction(
        account_id=data.from_account,
        type="DEBIT",
        amount=data.amount,
        description="UPI Transfer Debit"
    )

    credit = Transaction(
        account_id=data.to_account,
        type="CREDIT",
        amount=data.amount,
        description="UPI Transfer Credit"
    )

    db.add(debit)
    db.add(credit)
    db.commit()

    return {"message": "Transfer successful"}
class DepositRequest(BaseModel):
    account_id: int
    amount: float

@router.post("/deposit")
def deposit(data: DepositRequest, db: Session = Depends(get_db)):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    credit = Transaction(
        account_id=data.account_id,
        type="CREDIT",
        amount=data.amount,
        description="Account Deposit"
    )

    db.add(credit)
    db.commit()

    return {"message": "Amount deposited successfully"}
