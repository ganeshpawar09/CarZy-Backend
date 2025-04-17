from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user_schema import UserOut, UserNameUpdate, UserVerificationRequest, UserVerificationStatusUpdate
from models.user_model import User
from schemas.system_review_schema import PostSystemReview
from database import get_db
from datetime import datetime
from models.system_review_model import SystemReview

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


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

    user.verification_status = "in_process"
    user.license_photo_url= payload.license_photo_url
    user.passport_photo_url= payload.passport_photo_url


    db.commit()
    return {"message": "Verification request submitted",}

@router.post("/user-verification-update")
def update_verification_status(
    payload: UserVerificationStatusUpdate,
    db: Session = Depends(get_db)
):
    if payload.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.verification_status = payload.status
    user.last_verified_by=payload.verified_by
    
    if payload.status=="rejected":
        user.rejection_reason=payload.rejection_reason
    else:
        user.rejection_reason=""

    db.commit()
    return {"message": f"User verification {payload.status}"}

@router.post("/post-or-update-review")
def post_or_update_system_review(payload: PostSystemReview, db: Session=Depends(get_db)):

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    system_review = db.query(SystemReview).filter(SystemReview.user_id == payload.user_id).first()

    if system_review:
       
        system_review.rating = payload.rating
        system_review.description = payload.description
        system_review.updated_at = datetime.utcnow()
    else:
        system_review = SystemReview(
            user_id=payload.user_id,
            user_name=user.full_name,
            user_type=user.user_type,
            rating=payload.rating,
            description=payload.description,
        )
        db.add(system_review)
        db.flush()  # To get review.id before commit

        # Update user's review_id
        user = db.query(User).filter(User.id == payload.user_id).first()
        if user:
            user.review_id = system_review.id

    db.commit()
    db.refresh(system_review)
    return {
        "message": "System review successfully posted",
    }


