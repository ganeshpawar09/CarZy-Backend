from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, Date, DateTime
from datetime import datetime
from models.base import Base

class CarVerification(Base):
    __tablename__ = 'car_verification'

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('car.id'), nullable=True)  # Allowing nullable for new cars

    car_number = Column(Text, nullable=False)

    puc_image_url = Column(Text, nullable=False)
    puc_expiry_date = Column(Date, nullable=False)

    rc_image_url = Column(Text, nullable=False)
    rc_expiry_date = Column(Date, nullable=False)

    insurance_image_url = Column(Text, nullable=False)
    insurance_expiry_date = Column(Date, nullable=False)

    status = Column(Enum('pending', 'approved', 'rejected', 'cancelled'), default='pending')
    verified_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
