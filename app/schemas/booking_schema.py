from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BookingBase(BaseModel):
    user_id: int
    car_id: int
    start_datetime: datetime
    end_datetime: datetime
    pickup_location: str
    delivery_option: str
    cancelable_until: datetime
    status: Optional[str] = 'booked'
    total_price: float
    payment_id: Optional[int] = None
    created_at: Optional[datetime] = None

class BookingCreate(BookingBase):
    pass

class BookingOut(BookingBase):
    id: int

    class Config:
        orm_mode = True
