from sqlalchemy import Column, Integer, Float, DateTime, Enum, ForeignKey, Text, String
from datetime import datetime
from models.base import Base

class Refund(Base):
    __tablename__ = 'refund'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)             
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    
    reason = Column(Enum('cancelled_by_user', 'refundable', 'cancelled_by_owner'), nullable=False)

    deduction_amount = Column(Float, default=0)
    deduction_reason = Column(Text, nullable=True)
    refund_amount = Column(Float, nullable=True)
    claimed_at = Column(DateTime, nullable=True)
    
    upi_id = Column(String(100), nullable=True)
    status = Column(Enum('pending', 'in_process', 'claimed'), default='pending')  
    razorpay_payment_id = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

