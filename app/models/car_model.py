from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Enum, ForeignKey, Text
from datetime import datetime
from models.base import Base

class Car(Base):
    __tablename__ = 'car'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    company_name = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    car_number = Column(String(20), nullable=False)
    manufacture_year = Column(Integer, nullable=False)
    purchase_type = Column(Enum('new', 'used'), nullable=False)
    ownership_count = Column(Integer, default=1, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    car_rating = Column(Float, default=0, nullable=False)
    no_of_car_rating = Column(Float, default=0, nullable=False)
    location = Column(String(255), nullable=False)
    last_serviced_on = Column(Date, nullable=False)  
    fuel_type = Column(Enum('petrol', 'cng', 'diesel', 'electric'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    car_type = Column(Enum('sedan', 'suv', 'hatchback'), nullable=False)  
    transmission_type = Column(Enum('manual', 'automatic'), nullable=False)  
    future_booking_datetime = Column(Text, nullable=False) 


    front_view_image_url = Column(Text, nullable=True)
    rear_view_image_url = Column(Text, nullable=True)
    left_side_image_url = Column(Text, nullable=True)
    right_side_image_url = Column(Text, nullable=True)

    features = Column(Text, nullable=False)

    puc_image_url = Column(Text, nullable=False)
    puc_expiry_date = Column(Date, nullable=False)
    rc_image_url = Column(Text, nullable=False)
    rc_expiry_date = Column(Date, nullable=False)
    insurance_image_url = Column(Text, nullable=False)
    insurance_expiry_date = Column(Date, nullable=False)

    cancellations = Column(Integer, default=0, nullable=False)
    
    last_verification_id = Column(Integer, ForeignKey('car_verification.id'), nullable=True)
    verification_status = Column(Enum('pending', 'in_process', 'approved', 'rejected'), default='pending', nullable=False)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
