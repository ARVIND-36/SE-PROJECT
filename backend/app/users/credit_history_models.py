from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class CreditHistory(Base):
    __tablename__ = "credit_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False)  # LOAN_APPLIED / LOAN_APPROVED / LOAN_REJECTED / PAYMENT_DELAY / ACCOUNT_OPENED
    description = Column(String)
    impact_score = Column(Integer, default=0)  # Positive or negative impact on CIBIL
    event_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Credit Inquiry tracking
    inquiry_type = Column(String, nullable=True)  # HARD / SOFT
    related_loan_id = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="credit_history")
