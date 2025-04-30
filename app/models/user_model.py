from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from datetime import datetime
from models.base import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), default="Guest")
    mobile_number = Column(String(15), unique=True, nullable=False)
    user_type = Column(Enum('user', 'owner', 'admin', 'employee'), default='user')

    license_photo_url = Column(Text, nullable=True)
    passport_photo_url = Column(Text, nullable=True)

    last_verified_id = Column(Integer, ForeignKey('user_verification.id'), nullable=True)
    verification_status = Column(Enum('pending', 'approved', 'rejected', 'in_process'), default='pending')
    rejection_reason = Column(Text, nullable=True)

    system_review_id = Column(Integer, ForeignKey('system_review.id'), nullable=True) 

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

