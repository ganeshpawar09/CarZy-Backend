from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, Date, DateTime
from datetime import datetime
from models.base import Base

class CarVerification(Base):
    __tablename__ = 'car_verification'

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=True)  

    status = Column(Enum('pending', 'approved', 'rejected'), default='pending')
    verifier_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
