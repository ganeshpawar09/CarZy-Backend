from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, DateTime
from datetime import datetime
from models.base import Base

class UserVerification(Base):
    __tablename__ = 'user_verification'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    license_photo_url = Column(Text, nullable=False)
    passport_photo_url = Column(Text, nullable=False)

    status = Column(Enum('pending', 'approved', 'rejected', 'cancelled'), default='pending')
    verified_by = Column(Integer, ForeignKey('user.id'), nullable=True) 
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
