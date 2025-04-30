from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user_schema import UserOut, UserNameUpdate, VerificationCheckRequest, VerificationCheckResponse, UserVerificationRequest, UserVerificationStatusUpdate, RefundOut, PenaltyOut, PaymentOut, CouponOut, CarVerificationOut, UserVerificationOut
from models.user_model import User
from models.refund_model import Refund
from models.penalty_model import Penalty
from models.payment_model import Payment  
from models.coupon_model import Coupon  
from database import get_db
from datetime import datetime
from models.car_verification_model import CarVerification
from models.system_review_model import SystemReview
from models.user_verification_model import UserVerification
from typing import List

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/reviews")
def get_top_system_reviews(db: Session = Depends(get_db)):
    top_reviews = (
        db.query(SystemReview)
        .order_by(SystemReview.rating.desc(), SystemReview.created_at.desc())
        .limit(10)
        .all()
    )
    return top_reviews

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user

@router.get("/refunds/{user_id}", response_model=List[RefundOut])
def get_user_refunds(user_id: int, db: Session = Depends(get_db)):
    refunds = db.query(Refund).filter(Refund.user_id == user_id).all()
    return refunds

@router.get("/penalties/{user_id}", response_model=List[PenaltyOut])
def get_user_penalties(user_id: int, db: Session = Depends(get_db)):
    penalties = db.query(Penalty).filter(Penalty.user_id == user_id).all()
    return penalties

@router.get("/coupons/{user_id}", response_model=List[CouponOut])
def get_user_coupons(user_id: int, db: Session = Depends(get_db)):
    coupons = db.query(Coupon).filter(Coupon.user_id == user_id).all()
    return coupons

@router.get("/payments/{user_id}", response_model=List[PaymentOut])
def get_user_payments(user_id: int, db: Session = Depends(get_db)):
    payments = db.query(Payment).filter(Payment.user_id == user_id).all()
    return payments

@router.get("/coupon/{coupon_id}", response_model=float)
def get_coupon_discount(coupon_id: int, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(
        Coupon.id == coupon_id,
        Coupon.used == False  # Only unused coupons
    ).first()

    if not coupon:
        return -1.0  # Return -1 if coupon not found or already used
    
    return coupon.discount_percentage



@router.post("/user-verification-check", response_model=VerificationCheckResponse)
def check_verification_status(
    payload: VerificationCheckRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.verification_status == "rejected":
        return {
            "verification_status": user.verification_status,
            "rejection_reason": user.rejection_reason
        }

    return {
        "verification_status": user.verification_status
    }

@router.post("/update-name", response_model=UserOut)
def update_user_name(
    payload: UserNameUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name = payload.full_name
    db.commit()
    db.refresh(user)
    return user


@router.post("/user-verification")
def create_verification_request(
    payload: UserVerificationRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if there's an existing pending/in_process verification
    existing = db.query(UserVerification).filter(
        UserVerification.user_id == payload.user_id,
        UserVerification.status.in_(["pending", "in_process"])
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Verification already in process")

    # Create new verification request
    verification = UserVerification(
        user_id=payload.user_id,
        license_photo_url=payload.license_photo_url,
        passport_photo_url=payload.passport_photo_url,
        status='pending'
    )
    db.add(verification)

    user.verification_status = "in_process"
    db.commit()
    return {"message": "Verification request submitted"}


@router.post("/user-verification-cancel")
def cancel_verification_request(
    user_id: int,
    db: Session = Depends(get_db)
):
    verification = db.query(UserVerification).filter(
        UserVerification.user_id == user_id,
        UserVerification.status.in_(["pending", "in_process"])
    ).first()

    if not verification:
        raise HTTPException(status_code=404, detail="No active verification request found")

    verification.status = "cancelled"
    verification.updated_at = datetime.utcnow()

    # Reset user verification status
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.verification_status = "pending"
        user.last_verified_id = None
        user.rejection_reason = ""

    db.commit()
    return {"message": "Verification request cancelled successfully"}
