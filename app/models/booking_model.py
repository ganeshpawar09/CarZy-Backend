from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from datetime import datetime
from models.base import Base

class Booking(Base):
    __tablename__ = 'booking'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    
    pickup_delivery_location = Column(String(255), nullable=False)  
    latitude = Column(Float, nullable=True)  
    longitude = Column(Float, nullable=True)  
    
    status = Column(Enum('booked', 'cancelled', 'completed', 'picked', 'cancelled_by_owner'), default='booked')  
    total_price = Column(Float, nullable=False)

    picked_time = Column(DateTime, nullable=False) 
    returned_time = Column(DateTime, nullable=False)  
    price_per_hour = Column(Float, nullable=False)

    late_fees_charged=Column(Boolean, default=False, nullable=False)
    
    last_otp_id = Column(Integer, ForeignKey('otp.id'), nullable=True)  
    payment_id = Column(Integer, ForeignKey('payment.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
