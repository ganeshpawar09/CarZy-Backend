from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.payout_model import Payout
from schemas.user_schema import PayoutClaim, PenaltyPaymentUpdate, SystemReviewCreate, RefundClaimIn, SystemReviewOut, UserOut, UserNameUpdate, VerificationCheckRequest, VerificationCheckResponse, UserVerificationRequest, UserVerificationStatusUpdate, RefundOut, PenaltyOut, PaymentOut, CouponOut, CarVerificationOut, UserVerificationOut
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

@router.get("/get-system_review/{user_id}", response_model=SystemReviewOut)
def get_user_penalties(user_id: int, db: Session = Depends(get_db)):
    review = db.query(SystemReview).filter(SystemReview.user_id == user_id).first()
    return review

@router.post("/post-system-review")
def post_system_review(payload: SystemReviewCreate, db: Session = Depends(get_db)):
    # Fetch user from DB
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the user already has a system review
    existing_review = db.query(SystemReview).filter(SystemReview.user_id == user.id).first()

    if existing_review:
        # Update the existing review
        existing_review.rating = payload.rating
        existing_review.description = payload.description
        db.commit()
        db.refresh(existing_review)

        return {"message": "Review updated successfully"}
    else:
        # Create a new system review if none exists
        review = SystemReview(
            user_id=user.id,
            user_name=user.full_name,
            user_type=user.user_type,
            rating=payload.rating,
            description=payload.description
        )
        db.add(review)
        db.commit()
        db.refresh(review)

        # Link the review to the user
        user.system_review_id = review.id
        db.commit()

        return {"message": "Review submitted successfully"}


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

    existing = db.query(UserVerification).filter(
        UserVerification.user_id == payload.user_id,
        UserVerification.status.in_(["pending", "in_process"])
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Verification already in process")

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

@router.get("/payouts/{user_id}")
def get_payouts_by_user(user_id: int, db: Session = Depends(get_db)):
    payouts = db.query(Payout).filter(Payout.owner_id == user_id).order_by(Payout.created_at.desc()).all()
    return payouts

@router.put("/claim-refund")
def claim_refund(data: RefundClaimIn, db: Session = Depends(get_db)):
    refund = db.query(Refund).filter(Refund.id == data.refund_id).first()
    
    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")
    
    if refund.status == 'claimed':
        raise HTTPException(status_code=400, detail="Refund already claimed")
    
    # Mark the refund as in_process
    refund.status = 'in_process'
    refund.upi_id = data.upi_id
    refund.claimed_at = datetime.utcnow()  
    
    db.commit()
    db.refresh(refund)  
    
    return {"message": "Refund in process"}

@router.put("/claim-payout")
def claim_payout(data: PayoutClaim, db: Session = Depends(get_db)):
    payout = db.query(Payout).filter(Payout.id == data.payout_id).first()
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")

    if payout.status == "claimed":
        raise HTTPException(status_code=400, detail="Payout already claimed")

    payout.status = "in_process"
    payout.upi_id = data.upi_id
    payout.claimed_at = datetime.utcnow()

    db.commit()
    return {"message": "Payout in process"}


@router.put("/pay-penalty")
def update_penalty_payment(data: PenaltyPaymentUpdate, db: Session = Depends(get_db)):
    penalty = db.query(Penalty).filter(Penalty.id == data.penalty_id).first()

    if not penalty:
        raise HTTPException(status_code=404, detail="Penalty not found")

    if penalty.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Penalty is already marked as paid")

    penalty.payment_status = "paid"
    penalty.razorpay_payment_id = data.razorpay_payment_id
    db.commit()
    db.refresh(penalty)

    return {"message": "Penalty payment updated successfully", "penalty": penalty}