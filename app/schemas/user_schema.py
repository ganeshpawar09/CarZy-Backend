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

class SystemReviewCreate(BaseModel):
    user_id: int
    rating: int
    description: str

class UserVerificationStatusUpdate(BaseModel):
    user_id: int
    verifier_id: int
    verification_id: int
    status: str  
    rejection_reason: Optional[str] = None
    
class SystemReviewOut(BaseModel):
    user_id: int
    user_name: str
    user_type: str
    rating: int 
    description: str


class RefundOut(BaseModel):
    id: int
    user_id: int
    booking_id: int
    reason: str
    deduction_amount: float
    deduction_reason: Optional[str] = None
    refund_amount: Optional[float] = None
    claimed_at: Optional[datetime] = None
    upi_id: Optional[str] = None
    status: str
    razorpay_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PenaltyOut(BaseModel):
    id: int
    user_id: int
    booking_id: int
    penalty_amount: float
    penalty_reason: Optional[str] = None
    reason: str
    payment_status: str
    razorpay_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PaymentOut(BaseModel):
    id: int
    booking_id: Optional[int]
    user_id: int
    total_hours: float
    price_per_hour: float
    security_deposit: float
    coupon_discount: Optional[float]
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class CouponOut(BaseModel):
    id: int
    user_id: int
    discount: float
    used: bool
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

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RefundClaimIn(BaseModel):
    refund_id: int
    upi_id: str 

class PenaltyPaymentUpdate(BaseModel):
    penalty_id: int
    razorpay_payment_id: str

class PayoutClaim(BaseModel):
    payout_id: int
    upi_id: str