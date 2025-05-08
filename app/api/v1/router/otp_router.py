from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.user_model import User
from models.otp_model import Otp
from database import get_db
from schemas.otp_schema import OTPVerifyRequest, OTPRequest
from datetime import datetime, timedelta
import random
from schemas.user_schema import UserOut
from twilio.rest import Client
from utils.sms import send_sms 

router = APIRouter(prefix="/otp", tags=["Otp"])


@router.post("/send-otp")
def send_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    otp = str(random.randint(1000, 9999))
    otp_entry = Otp(
        mobile_number=payload.mobile_number,
        otp=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        created_at=datetime.utcnow()
    )
    db.add(otp_entry)
    db.commit()
    db.refresh(otp_entry)
    
    # if(payload.mobile_number!="1111111111" and payload.mobile_number!="2222222222"):
    #     send_sms("+91"+payload.mobile_number, f"Your CarZy OTP is {otp}")
    print(f"OTP for {payload.mobile_number}: {otp}")
    return {
        "message": "OTP sent successfully",
        "otp_id": otp_entry.id
    }

@router.post("/verify-otp", response_model=UserOut)
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    otp_entry = db.query(Otp).filter(
        Otp.id == payload.otp_id,
        Otp.otp == payload.otp
    ).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP ID")

    if otp_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")

    if otp_entry.verified_at:
        raise HTTPException(status_code=400, detail="OTP has already been used")

    if payload.user_id:
        # Update the existing user's mobile number
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.mobile_number = otp_entry.mobile_number
    else:
        # Check if user already exists with this mobile number
        user = db.query(User).filter(User.mobile_number == otp_entry.mobile_number).first()
        if not user:
            user = User(mobile_number=otp_entry.mobile_number)
            db.add(user)
            db.commit()
            db.refresh(user)

    otp_entry.verified_at = datetime.utcnow()
    db.commit()

    return user
