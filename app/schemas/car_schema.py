from pydantic import BaseModel
from typing import Optional
from typing import Optional, Literal
from datetime import date, datetime

class CarVerificationRequest(BaseModel):
    car_id: Optional[int] = None
    owner_id: int
    company_name: str
    model_name: str
    car_number: str
    manufacture_year: int
    purchase_type: Literal['new', 'used']
    ownership_count: int = 1
    price_per_hour: float
    location: str
    fuel_type: Literal['petrol', 'cng', 'diesel', 'electric']
    features: str
    car_type: str  # Keep this only once
    transmission_type: str  # Keep this only once
    front_view_image_url: str
    rear_view_image_url: str
    left_side_image_url: str
    right_side_image_url: str
    last_serviced_on: date
    puc_image_url: str
    puc_expiry_date: date
    rc_image_url: str
    rc_expiry_date: date
    insurance_image_url: str
    insurance_expiry_date: date
    future_booking_datetime: Optional[str] = None
    latitude: float
    longitude: float
    is_visible: bool

    class Config:
        orm_mode = True


class CarOut(BaseModel):
    id: int 
    owner_id: int 
    company_name: str
    model_name: str
    car_number: str
    manufacture_year: int
    purchase_type: Literal['new', 'used']
    ownership_count: int
    price_per_hour: float
    car_rating: float
    no_of_car_rating: float
    location: str
    fuel_type: Literal['petrol', 'cng', 'diesel', 'electric']
    latitude: float  
    longitude: float 
    is_visible: bool
    future_booking_datetime: Optional[str]=None
    car_type: str
    transmission_type: str
    front_view_image_url: str
    rear_view_image_url: str
    left_side_image_url: str
    right_side_image_url: str
    last_serviced_on: Optional[date]
    features: str

    puc_image_url: str
    puc_expiry_date: date
    rc_image_url: str
    rc_expiry_date: date
    insurance_image_url: str
    insurance_expiry_date: date

    last_verification_id: Optional[int]=None
    verification_status: Literal['pending', 'in_process', 'approved', 'rejected']
    rejection_reason: Optional[str]=None

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CarVerificationRequestStatusUpdate(BaseModel):
    verification_id: int
    status: str  
    verifier_id: int 
    rejection_reason: Optional[str] = None


class CarVisibilityChangeRequest(BaseModel):
    car_id: int


class CarSearchRequest(BaseModel):
    latitude: float
    longitude: float
    startDateTime: datetime
    endDateTime: datetime
    distance: Optional[float] = 100  # km
    carType: Optional[str] = None
    transmission: Optional[str] = None
    fuelType: Optional[str] = None
    minRating: Optional[float] = None
    sortBy: Optional[str] = "nearest" 

    class Config:
        from_attributes = True

class CarSearchResponse(BaseModel):
    id: int 
    owner_id: int 
    distance: Optional[float] = None
    company_name: str
    model_name: str
    car_number: str
    manufacture_year: int
    purchase_type: Literal['new', 'used']
    ownership_count: int
    price_per_hour: float
    car_rating: float
    no_of_car_rating: float
    location: str
    fuel_type: Literal['petrol', 'cng', 'diesel', 'electric']
    latitude: float  
    longitude: float 
    is_visible: bool
    future_booking_datetime: Optional[str]=None
    car_type: str
    transmission_type: str
    front_view_image_url: str
    rear_view_image_url: str
    left_side_image_url: str
    right_side_image_url: str
    last_serviced_on: Optional[date]
    features: str

    puc_image_url: str
    puc_expiry_date: date
    rc_image_url: str
    rc_expiry_date: date
    insurance_image_url: str
    insurance_expiry_date: date

    last_verification_id: Optional[int]=None
    verification_status: Literal['pending', 'in_process', 'approved', 'rejected']
    rejection_reason: Optional[str]=None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True