from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from models.base import Base

class CarReview(Base):
    __tablename__ = 'car_review'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)
    rating = Column(Integer, nullable= False)
    review_text = Column(Text, nullable= False)
