from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timezone, timedelta
from app.db.base import Base

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    purpose = Column(String, nullable=False)  # REGISTRATION / LOGIN / PASSWORD_RESET
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    
    def is_expired(self):
        """Check if OTP is expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    @staticmethod
    def generate_expiry():
        """Generate expiry time (5 minutes from now)"""
        return datetime.now(timezone.utc) + timedelta(minutes=5)
