from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)   # CREDIT / DEBIT
    amount = Column(Float, nullable=False)
    description = Column(String)
    balance_after = Column(Float, nullable=False)  # Balance after transaction
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
