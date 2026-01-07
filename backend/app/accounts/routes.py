from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.auth.dependencies import get_current_user
from .models import Account
import uuid

router = APIRouter(prefix="/accounts", tags=["Accounts"])

class AccountCreate(BaseModel):
    account_type: str

@router.post("/create")
def create_account(data: AccountCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new account for authenticated user"""
    account = Account(
        account_number=str(uuid.uuid4())[:12],
        account_type=data.account_type,
        user_id=current_user["user_id"],
        balance=0.0
    )
    db.add(account)
    db.commit()
    return {"message": "Account created", "account_number": account.account_number}

@router.get("/")
def get_accounts(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all accounts for authenticated user"""
    return db.query(Account).filter(Account.user_id == current_user["user_id"]).all()

@router.get("/balance/{account_id}")
def get_balance(account_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get account balance for authenticated user's account"""
    acc = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user["user_id"]
    ).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": acc.id, "balance": acc.balance, "status": acc.status}

@router.post("/freeze")
def freeze_account(account_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Freeze account - requires employee role"""
    if current_user.get("role") != "employee":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    acc.status = "FROZEN"
    db.commit()
    return {"message": "Account frozen"}

@router.post("/unfreeze")
def unfreeze_account(account_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Unfreeze account - requires employee role"""
    if current_user.get("role") != "employee":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    acc.status = "ACTIVE"
    db.commit()
    return {"message": "Account unfrozen"}
