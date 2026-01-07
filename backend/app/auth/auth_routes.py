from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from app.db.database import get_db
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.email_service import send_otp_email, generate_otp, validate_pan_format
from app.auth.otp_models import OTP
from app.users.models import User
from app.accounts.models import Account
from datetime import datetime, timezone
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ============= REGISTRATION WITH OTP =============

class RegistrationInit(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    pan_number: str
    date_of_birth: str  # YYYY-MM-DD
    address: str
    monthly_income: float
    employment_status: str
    
    @validator('pan_number')
    def validate_pan(cls, v):
        if not validate_pan_format(v):
            raise ValueError('Invalid PAN format. Must be: ABCDE1234F')
        return v.upper()
    
    @validator('employment_status')
    def validate_employment(cls, v):
        allowed = ['EMPLOYED', 'SELF_EMPLOYED', 'UNEMPLOYED', 'RETIRED']
        if v.upper() not in allowed:
            raise ValueError(f'Employment status must be one of: {allowed}')
        return v.upper()

class RegistrationComplete(BaseModel):
    email: EmailStr
    otp: str
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter')
        return v

@router.post("/register/init")
def register_init(data: RegistrationInit, db: Session = Depends(get_db)):
    """
    Step 1: Initiate registration with user details
    - Validates PAN card
    - Sends OTP to email
    """
    
    # Check if email already registered
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if PAN already registered
    existing_pan = db.query(User).filter(User.pan_number == data.pan_number).first()
    if existing_pan:
        raise HTTPException(status_code=400, detail="PAN number already registered")
    
    # Generate and send OTP
    otp_code = generate_otp()
    
    # Delete old OTPs for this email
    db.query(OTP).filter(OTP.email == data.email, OTP.purpose == "REGISTRATION").delete()
    
    # Save OTP
    new_otp = OTP(
        email=data.email,
        otp_code=otp_code,
        purpose="REGISTRATION",
        expires_at=OTP.generate_expiry()
    )
    db.add(new_otp)
    db.commit()
    
    # Send OTP email
    send_otp_email(data.email, otp_code, "REGISTRATION")
    
    return {
        "message": "OTP sent to your email",
        "email": data.email,
        "valid_for": "5 minutes"
    }

@router.post("/register/verify")
def register_verify(data: RegistrationComplete, registration_data: RegistrationInit, db: Session = Depends(get_db)):
    """
    Step 2: Complete registration after OTP verification
    - Verifies OTP
    - Creates user account
    - Generates account number
    """
    
    # Verify OTP
    otp_record = db.query(OTP).filter(
        OTP.email == data.email,
        OTP.otp_code == data.otp,
        OTP.purpose == "REGISTRATION",
        OTP.is_verified == False
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if otp_record.is_expired():
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one")
    
    # Mark OTP as verified
    otp_record.is_verified = True
    
    # Generate unique username from email
    username_base = data.email.split('@')[0]
    username = username_base
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{username_base}{counter}"
        counter += 1
    
    # Create user
    new_user = User(
        username=username,
        hashed_password=hash_password(data.password),
        role="customer",
        full_name=registration_data.full_name,
        email=data.email,
        phone=registration_data.phone,
        address=registration_data.address,
        date_of_birth=datetime.strptime(registration_data.date_of_birth, "%Y-%m-%d").date(),
        pan_number=registration_data.pan_number,
        monthly_income=registration_data.monthly_income,
        employment_status=registration_data.employment_status
    )
    db.add(new_user)
    db.flush()  # Get user.id
    
    # Create default savings account
    account_number = f"ACC{str(uuid.uuid4().int)[:12]}"
    new_account = Account(
        account_number=account_number,
        account_type="savings",
        status="ACTIVE",
        balance=0.0,
        user_id=new_user.id
    )
    db.add(new_account)
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"user_id": new_user.id, "role": new_user.role})
    
    return {
        "message": "Registration successful",
        "account_number": account_number,
        "username": username,
        "access_token": access_token,
        "token_type": "bearer"
    }

# ============= LOGIN WITH ACCOUNT NUMBER & OTP =============

class LoginInit(BaseModel):
    account_number: str
    
@router.post("/login/init")
def login_init(data: LoginInit, db: Session = Depends(get_db)):
    """
    Step 1: Initiate login with account number
    - Sends OTP to registered email
    """
    
    # Find account
    account = db.query(Account).filter(Account.account_number == data.account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get user
    user = db.query(User).filter(User.id == account.user_id).first()
    if not user or not user.email:
        raise HTTPException(status_code=400, detail="Email not registered for this account")
    
    # Generate and send OTP
    otp_code = generate_otp()
    
    # Delete old OTPs
    db.query(OTP).filter(OTP.email == user.email, OTP.purpose == "LOGIN").delete()
    
    # Save OTP
    new_otp = OTP(
        email=user.email,
        otp_code=otp_code,
        purpose="LOGIN",
        expires_at=OTP.generate_expiry()
    )
    db.add(new_otp)
    db.commit()
    
    # Send OTP
    send_otp_email(user.email, otp_code, "LOGIN")
    
    # Mask email
    email_parts = user.email.split('@')
    masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}"
    
    return {
        "message": "OTP sent to your registered email",
        "email": masked_email,
        "valid_for": "5 minutes"
    }

class LoginComplete(BaseModel):
    account_number: str
    otp: str

@router.post("/login/verify")
def login_verify(data: LoginComplete, db: Session = Depends(get_db)):
    """
    Step 2: Complete login with OTP verification
    - Verifies OTP
    - Returns access token
    """
    
    # Find account
    account = db.query(Account).filter(Account.account_number == data.account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Get user
    user = db.query(User).filter(User.id == account.user_id).first()
    
    # Verify OTP
    otp_record = db.query(OTP).filter(
        OTP.email == user.email,
        OTP.otp_code == data.otp,
        OTP.purpose == "LOGIN",
        OTP.is_verified == False
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if otp_record.is_expired():
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one")
    
    # Mark OTP as verified
    otp_record.is_verified = True
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"user_id": user.id, "role": user.role})
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "name": user.full_name,
            "email": user.email,
            "account_number": account.account_number
        }
    }

# ============= RESEND OTP =============

class ResendOTP(BaseModel):
    email: EmailStr
    purpose: str  # REGISTRATION or LOGIN

@router.post("/otp/resend")
def resend_otp(data: ResendOTP, db: Session = Depends(get_db)):
    """Resend OTP to email"""
    
    # Generate new OTP
    otp_code = generate_otp()
    
    # Delete old OTPs
    db.query(OTP).filter(OTP.email == data.email, OTP.purpose == data.purpose).delete()
    
    # Save new OTP
    new_otp = OTP(
        email=data.email,
        otp_code=otp_code,
        purpose=data.purpose,
        expires_at=OTP.generate_expiry()
    )
    db.add(new_otp)
    db.commit()
    
    # Send OTP
    send_otp_email(data.email, otp_code, data.purpose)
    
    return {
        "message": "New OTP sent to your email",
        "valid_for": "5 minutes"
    }
