from sqlalchemy import Column, Integer, Float, DateTime, Enum, ForeignKey, Text
from datetime import datetime
from models.base import Base

class Penalty(Base):
    __tablename__ = 'penalty'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(Enum('late_return', 'cancelled_by_owner'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
