from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import declarative_base
from app.db.database import engine

Base = declarative_base()

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    status = Column(String, default="PENDING")  # PENDING / APPROVED / REJECTED
    cibil_score = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)
