from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from datetime import datetime
from models.base import Base

class SystemReview(Base):
    __tablename__ = 'system_review'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)  
    user_name = Column(String(100), nullable=False)
    user_type = Column(Enum('user', 'owner'), nullable=False)
    rating = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
