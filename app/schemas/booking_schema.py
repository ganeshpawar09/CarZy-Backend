from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookingRequest(BaseModel):
    user_id: int
    car_id: int
    car_owner_id: int
    start_datetime: datetime
    end_datetime: datetime

    pickup_delivery_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    total_amount: float
    price_per_hour: float
    total_hours: float
    security_deposit: float
    coupon_discount: Optional[float] = None
    coupon_id: Optional[int] = None
    razorpay_payment_id: Optional[str] = None


class MyBookingOut(BaseModel):
    id: int
    user_id: int
    car_id: int
    car_owner_id: int
    start_datetime: datetime
    end_datetime: datetime

    pickup_delivery_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str

    picked_time: Optional[datetime] = None
    returned_time: Optional[datetime] = None

    total_amount: float
    price_per_hour: float
    total_hours: float
    security_deposit: float
    coupon_discount: Optional[float] = None

    late_fees_charged: Optional[bool] = None
    late_fees_amount: Optional[float] = None


class MyCarBookingOut(BaseModel):
    id: int
    user_id: int
    car_id: int
    car_owner_id: int
    start_datetime: datetime
    end_datetime: datetime

    pickup_delivery_location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str

    total_amount: float
    price_per_hour: float
    total_hours: float
    security_deposit: float
    coupon_discount: Optional[float] = None

    
    picked_time: Optional[datetime] = None
    returned_time: Optional[datetime] = None
    late_fees_charged: Optional[bool] = None
    late_fees_amount: Optional[float] = None
    pickup_otp: str
    drop_otp: str



class PickupConfirmation(BaseModel):
    booking_id: int
    otp: str
    before_front_image_url: Optional[str] = None
    before_rear_image_url: Optional[str] = None
    before_left_side_image_url: Optional[str] = None
    before_right_side_image_url: Optional[str] = None
    before_interior_image_url: Optional[str] = None

class DropConfirmation(BaseModel):
    booking_id: int
    otp: str
    after_front_image_url: Optional[str] = None
    after_rear_image_url: Optional[str] = None
    after_left_side_image_url: Optional[str] = None
    after_right_side_image_url: Optional[str] = None
    after_interior_image_url: Optional[str] = None


class BookingCancellationByOwner(BaseModel):
    booking_id: int  
    owner_id: int    

class BookingCancellation(BaseModel):
    booking_id: int  
    user_id: int 
    refund_percentage: Optional[float] = None


# Request model for Razorpay order creation
class RazorpayOrderRequest(BaseModel):
    amount: float  # Amount in paise (1 INR = 100 paise)
    currency: str = "INR"
    receipt: Optional[str] = None
    notes: Optional[dict] = None

# Request model for payment verification
class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str