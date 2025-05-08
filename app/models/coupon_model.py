from sqlalchemy import Column, Integer, Float, DateTime, Boolean, ForeignKey, Text, String
from datetime import datetime
from models.base import Base

class Coupon(Base):
    __tablename__ = 'coupon'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    discount = Column(Float, nullable=False)
    used= Column(Boolean, default=False, nullable=False)  

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

