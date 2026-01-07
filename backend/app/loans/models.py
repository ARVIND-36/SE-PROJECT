from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    loan_term_months = Column(Integer, nullable=False)  # Loan duration in months
    monthly_emi = Column(Float, nullable=False)
    outstanding_amount = Column(Float, nullable=False)
    status = Column(String, default="PENDING")  # PENDING / APPROVED / REJECTED / CLOSED
    cibil_score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="loans")
    repayments = relationship("LoanRepayment", back_populates="loan", cascade="all, delete-orphan")
