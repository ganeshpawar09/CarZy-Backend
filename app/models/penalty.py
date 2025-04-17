from sqlalchemy import Column, Integer, Float, DateTime, Enum, ForeignKey, Text
from datetime import datetime
from models.base import Base

class Penalty(Base):
    __tablename__ = 'penalty'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    reason = Column(Text, nullable=False)  # e.g., "owner cancelled last minute"
    amount = Column(Float, nullable=False)  # Penalty amount imposed
    created_at = Column(DateTime, default=datetime.utcnow)
