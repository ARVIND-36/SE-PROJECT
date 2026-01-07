from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class LoanRepayment(Base):
    __tablename__ = "loan_repayments"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    emi_amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=False)
    is_delayed = Column(Boolean, default=False)
    days_delayed = Column(Integer, default=0)
    status = Column(String, default="PENDING")  # PENDING / PAID / DEFAULTED
    penalty_amount = Column(Float, default=0.0)
    
    # Relationships
    loan = relationship("Loan", back_populates="repayments")
