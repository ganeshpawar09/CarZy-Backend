from sqlalchemy import Column, Integer, Float, DateTime, Enum, ForeignKey, Text, String
from datetime import datetime
from models.base import Base

class Penalty(Base):
    __tablename__ = 'penalty'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)

    penalty_amount = Column(Float, nullable=False)
    penalty_reason = Column(Text, nullable=True)
    reason = Column(Enum('late_drop', 'cancelled_by_owner'), nullable=False)

    payment_status = Column(Enum('unpaid', 'paid'), default='unpaid', nullable=False)
    razorpay_payment_id = Column(String(100), nullable=True) 

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
