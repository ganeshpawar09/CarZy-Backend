from sqlalchemy import Column, Integer, Text, String, Float, DateTime, Enum, ForeignKey, Boolean
from datetime import datetime
from models.base import Base

class Booking(Base):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=False)
    car_owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    
    pickup_delivery_location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    review_id = Column(Integer, ForeignKey('car_review.id'), nullable=True) 

    status = Column(Enum('booked', 'completed', 'picked', 'cancelled_by_user','cancelled_by_owner', 'cancelled_by_system'), default='booked')

    payment_id = Column(Integer, ForeignKey("payment.id"))
    
    total_hours = Column(Float, nullable=False, default=0) 
    price_per_hour = Column(Float, nullable=False)
    
    security_deposit = Column(Float, nullable=False)
    coupon_discount = Column(Float, nullable=True, default=0)
    late_charge = Column(Float, nullable=True, default=0)

    picked_time = Column(DateTime, nullable=True)
    returned_time = Column(DateTime, nullable=True)

    pickup_otp = Column(String(10), nullable=True)
    pickup_otp_used = Column(Boolean, default=False)

    drop_otp = Column(String(10), nullable=True)
    drop_otp_used = Column(Boolean, default=False)

    before_front_image_url = Column(Text, nullable=True)
    before_rear_image_url = Column(Text, nullable=True)
    before_left_side_image_url = Column(Text, nullable=True)
    before_right_side_image_url = Column(Text, nullable=True)

    after_front_image_url = Column(Text, nullable=True)
    after_rear_image_url = Column(Text, nullable=True)
    after_left_side_image_url = Column(Text, nullable=True)
    after_right_side_image_url = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
