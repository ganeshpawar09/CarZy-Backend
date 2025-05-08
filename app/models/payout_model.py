from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Boolean
from datetime import datetime
from models.base import Base

class Payout(Base):
    __tablename__ = 'payout'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)  
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=False)

    total_hours = Column(Float, nullable=False, default=0) 
    price_per_hour = Column(Float, nullable=False)
    coupon_discount = Column(Float, nullable=True, default=0)
    late_charge = Column(Float, nullable=True, default=0)
    payout_amount = Column(Float, nullable=True, default=0)
    
    status = Column(Enum('pending', "in_process", 'claimed', ), default='pending')

    upi_id = Column(String(100), nullable=True)  
    razorpay_payment_id = Column(String(100), nullable=True)
    claimed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
