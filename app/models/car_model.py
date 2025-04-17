from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Enum, ForeignKey, Text
from datetime import datetime
from models.base import Base

class Car(Base):
    __tablename__ = 'car'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    company_name = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    car_number = Column(String(10), nullable=False)
    manufacture_year = Column(Integer, nullable=False)
    purchase_type = Column(Enum('new', 'used'), nullable=False)
    ownership_count = Column(Integer, default=1)
    price_per_hour = Column(Float, nullable=False)
    car_rating = Column(Float, default=0)
    no_of_car_rating = Column(Float, default=0)
    location = Column(String(255), nullable=False)
    last_serviced_on = Column(Date, nullable=True)  
    fuel_type = Column(Enum('petrol', 'cng', 'diesel', 'electric'), nullable=False) 
    latitude = Column(Float, nullable=True) 
    longitude = Column(Float, nullable=True)  
    is_visible = Column(Boolean, default=True)

    future_booking_datetime = Column(Text, nullable=True) 

    front_view_image_url = Column(Text, nullable=True)
    rear_view_image_url = Column(Text, nullable=True)
    left_side_image_url = Column(Text, nullable=True)
    right_side_image_url = Column(Text, nullable=True)
    diagonal_front_left_image_url = Column(Text, nullable=True)
    diagonal_rear_right_image_url = Column(Text, nullable=True)
    dashboard_image_url = Column(Text, nullable=True)
    speedometer_fuel_gauge_image_url = Column(Text, nullable=True)
    front_seats_image_url = Column(Text, nullable=True)
    rear_seats_image_url = Column(Text, nullable=True)
    boot_space_image_url = Column(Text, nullable=True)
    tyre_condition_image_url = Column(Text, nullable=True)


    features = Column(Text, nullable=False)

    puc_image_url = Column(Text, nullable=True)
    puc_expiry_date = Column(Date, nullable=True)
    rc_image_url = Column(Text, nullable=True)
    rc_expiry_date = Column(Date, nullable=True)
    insurance_image_url = Column(Text, nullable=True)
    insurance_expiry_date = Column(Date, nullable=True)
    
    last_verified_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    verification_status = Column(Enum('pending', 'in_process', 'approved', 'rejected'), default='pending')
    rejection_reason = Column(Text, nullable=True)


    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
