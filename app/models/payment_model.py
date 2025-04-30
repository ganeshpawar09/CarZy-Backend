from sqlalchemy import Column, Integer, Float, DateTime, Enum, ForeignKey, Boolean
from datetime import datetime
from models.base import Base

class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    total_hours = Column(Float, nullable=False, default=0) 
    price_per_hour = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    security_deposit = Column(Float, nullable=False)
    coupon_discount = Column(Float, nullable=True, default=0)

    status = Column(Enum('pending', 'paid', 'failed', 'refunded', name='payment_status'), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
