from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from app.db.database import engine

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, nullable=False)
    account_type = Column(String, nullable=False)  # savings / current
    status = Column(String, default="ACTIVE")      # ACTIVE / FROZEN
    user_id = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)
