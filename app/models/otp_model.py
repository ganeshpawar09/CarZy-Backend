from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timedelta
from models.base import Base

class Otp(Base):
    __tablename__ = 'otp'

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String(15), nullable=False)
    otp = Column(String(6), nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)  # New
