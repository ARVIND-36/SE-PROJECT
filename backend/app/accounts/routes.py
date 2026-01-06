from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from .models import Account
import uuid

router = APIRouter(prefix="/accounts", tags=["Accounts"])

class AccountCreate(BaseModel):
    account_type: str

@router.post("/create")
def create_account(data: AccountCreate, user_id: int, db: Session = Depends(get_db)):
    account = Account(
        account_number=str(uuid.uuid4())[:12],
        account_type=data.account_type,
        user_id=user_id
    )
    db.add(account)
    db.commit()
    return {"message": "Account created", "account_number": account.account_number}

@router.get("/")
def get_accounts(user_id: int, db: Session = Depends(get_db)):
    return db.query(Account).filter(Account.user_id == user_id).all()

@router.post("/freeze")
def freeze_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    acc.status = "FROZEN"
    db.commit()
    return {"message": "Account frozen"}

@router.post("/unfreeze")
def unfreeze_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    acc.status = "ACTIVE"
    db.commit()
    return {"message": "Account unfrozen"}
