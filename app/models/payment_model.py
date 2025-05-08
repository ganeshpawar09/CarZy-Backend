from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Boolean
from datetime import datetime
from models.base import Base

class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    total_hours = Column(Float, nullable=False, default=0) 
    price_per_hour = Column(Float, nullable=False)
    
    security_deposit = Column(Float, nullable=False)
    coupon_discount = Column(Float, nullable=True, default=0)

    razorpay_payment_id = Column(String(255), nullable=True)

    status = Column(Enum('pending', 'paid', 'failed'), default='pending')
   
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
