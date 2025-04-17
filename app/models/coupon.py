from sqlalchemy import Column, Integer, Float, DateTime, Boolean, ForeignKey, Text, String
from datetime import datetime
from models.base import Base

class Coupon(Base):
    __tablename__ = 'coupon'

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    discount_amount = Column(Float, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    issued_for_reason = Column(Text, nullable=True)  # e.g., "owner cancelled trip"

    created_at = Column(DateTime, default=datetime.utcnow)
