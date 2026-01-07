from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # customer / employee
    
    # Profile Information for CIBIL
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    pan_number = Column(String, unique=True, nullable=True)
    
    # Financial Information
    monthly_income = Column(Float, default=0.0)
    employment_status = Column(String, default="UNEMPLOYED")  # EMPLOYED / SELF_EMPLOYED / UNEMPLOYED
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    credit_history = relationship("CreditHistory", back_populates="user", cascade="all, delete-orphan")
