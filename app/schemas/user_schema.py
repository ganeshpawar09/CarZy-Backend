from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class VerificationCheckRequest(BaseModel):
    user_id: int

class VerificationCheckResponse(BaseModel):
    verification_status: str
    rejection_reason: Optional[str] = None

class UserNameUpdate(BaseModel):
    user_id: int
    full_name: str
    
class UserOut(BaseModel):
    id: int
    full_name: Optional[str] = "Guest"
    mobile_number: str
    user_type: str

    license_photo_url: Optional[str] = None
    passport_photo_url: Optional[str] = None
    system_review_id: Optional[int] = None

    verification_status : str
    rejection_reason : Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserVerificationRequest(BaseModel):
    user_id:int
    license_photo_url: str
    passport_photo_url: str

class UserVerificationStatusUpdate(BaseModel):
    user_id: int
    verified_by: int
    verification_id: int
    status: str  
    rejection_reason: Optional[str] = None
    

class RefundOut(BaseModel):
    id: int
    user_id: int
    booking_id: int
    reason: str
    deduction_amount: float
    deduction_reason: Optional[str]
    refund_amount: Optional[float]
    created_at: datetime

    class Config:
        orm_mode = True

class PenaltyOut(BaseModel):
    id: int
    user_id: int
    booking_id: int
    amount: float
    reason: str
    created_at: datetime

    class Config:
        orm_mode = True

class PaymentOut(BaseModel):
    id: int
    booking_id: Optional[int]
    user_id: int
    total_hours: float
    price_per_hour: float
    total_amount: float
    security_deposit: float
    coupon_discount: Optional[float]
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class CouponOut(BaseModel):
    id: int
    user_id: int
    discount_percentage: float
    used: bool
    issued_for_reason: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True

class UserVerificationOut(BaseModel):
    id: int
    user_id: int
    license_photo_url: str
    passport_photo_url: str
    
    created_at: datetime
    updated_at: datetime

class CarVerificationOut(BaseModel):
    id: int
    car_id: Optional[int]
    car_number: str

    puc_image_url: str
    puc_expiry_date: date

    rc_image_url: str
    rc_expiry_date: date

    insurance_image_url: str
    insurance_expiry_date: date

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True