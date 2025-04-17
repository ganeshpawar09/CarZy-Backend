from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    status: str  
    rejection_reason: Optional[str] = None
    