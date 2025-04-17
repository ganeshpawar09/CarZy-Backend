from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date

class CarVerificationRequest(BaseModel):
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

    front_view_image_url: Optional[str] = None
    rear_view_image_url: Optional[str] = None
    left_side_image_url: Optional[str] = None
    right_side_image_url: Optional[str] = None
    diagonal_front_left_image_url: Optional[str] = None
    diagonal_rear_right_image_url: Optional[str] = None
    dashboard_image_url: Optional[str] = None
    speedometer_fuel_gauge_image_url: Optional[str] = None
    front_seats_image_url: Optional[str] = None
    rear_seats_image_url: Optional[str] = None
    boot_space_image_url: Optional[str] = None
    tyre_condition_image_url: Optional[str] = None

    puc_image_url: Optional[str] = None
    puc_expiry_date: Optional[date] = None
    rc_image_url: Optional[str] = None
    rc_expiry_date: Optional[date] = None
    insurance_image_url: Optional[str] = None
    insurance_expiry_date: Optional[date] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    is_visible: Optional[bool] = True


class CarVerificationRequestStatusUpdate(BaseModel):
    status: str  
    car_id: int
    verified_by: int
    rejection_reason: Optional[str] = None


class CarVisibilityChangeRequest(BaseModel):
    car_id: int
    owner_id: int
    is_visible: bool
