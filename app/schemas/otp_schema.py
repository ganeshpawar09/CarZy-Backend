from pydantic import BaseModel
from typing import Optional

class OTPRequest(BaseModel):
    mobile_number: str

class OTPVerifyRequest(BaseModel):
    otp_id: int
    otp: str
    user_id: Optional[int] = None
        
