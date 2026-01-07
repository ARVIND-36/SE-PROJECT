from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.auth.dependencies import get_current_user
from .models import Transaction
from app.accounts.models import Account
from datetime import date

router = APIRouter(prefix="/transactions", tags=["Transactions"])

class TransferRequest(BaseModel):
    from_account: int
    to_account: int
    amount: float

def update_account_balance(account_id: int, amount: float, transaction_type: str, db: Session):
    """Update account balance based on transaction type"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if transaction_type == "CREDIT":
        account.balance += amount
    else:  # DEBIT
        if account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        account.balance -= amount
    
    db.commit()
    return account.balance

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
def transfer(data: TransferRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Transfer money between accounts"""
    
    # Verify sender owns the from_account
    sender = db.query(Account).filter(
        Account.id == data.from_account,
        Account.user_id == current_user["user_id"]
    ).first()
    
    if not sender:
        raise HTTPException(status_code=403, detail="Unauthorized - account not found")
    
    if sender.status == "FROZEN":
        raise HTTPException(status_code=403, detail="Account is frozen")
    
    # Check daily withdrawal limit
    today_total = today_debit_total(data.from_account, db)
    if today_total + data.amount > DAILY_LIMIT:
        raise HTTPException(status_code=400, detail="Daily withdrawal limit exceeded")
    
    # Check if recipient account exists
    recipient = db.query(Account).filter(Account.id == data.to_account).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient account not found")
    
    if sender.balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Debit from sender
    sender.balance -= data.amount
    debit = Transaction(
        account_id=data.from_account,
        type="DEBIT",
        amount=data.amount,
        description=f"Transfer to {recipient.account_number}",
        balance_after=sender.balance
    )
    
    # Credit to recipient
    recipient.balance += data.amount
    credit = Transaction(
        account_id=data.to_account,
        type="CREDIT",
        amount=data.amount,
        description=f"Transfer from {sender.account_number}",
        balance_after=recipient.balance
    )
    
    db.add(debit)
    db.add(credit)
    db.commit()
    
    return {
        "message": "Transfer successful",
        "new_balance": sender.balance
    }

class DepositRequest(BaseModel):
    account_id: int
    amount: float

@router.post("/deposit")
def deposit(data: DepositRequest, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deposit money into account"""
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    # Verify user owns the account
    account = db.query(Account).filter(
        Account.id == data.account_id,
        Account.user_id == current_user["user_id"]
    ).first()
    
    if not account:
        raise HTTPException(status_code=403, detail="Unauthorized - account not found")
    
    account.balance += data.amount
    credit = Transaction(
        account_id=data.account_id,
        type="CREDIT",
        amount=data.amount,
        description="Cash Deposit",
        balance_after=account.balance
    )
    
    db.add(credit)
    db.commit()
    
    return {
        "message": "Amount deposited successfully",
        "new_balance": account.balance
    }

@router.get("/history/{account_id}")
def get_transaction_history(account_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get transaction history for an account"""
    
    # Verify user owns the account
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user["user_id"]
    ).first()
    
    if not account:
        raise HTTPException(status_code=403, detail="Unauthorized - account not found")
    
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.created_at.desc()).all()
    
    return transactions
