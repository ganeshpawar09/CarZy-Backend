from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user_schema import  UserVerificationStatusUpdate, CarVerificationOut, UserVerificationOut
from models.user_model import User
from database import get_db
from datetime import datetime
from models.car_verification_model import CarVerification
from models.user_verification_model import UserVerification
from models.car_model import Car
from typing import List
from schemas.car_schema import CarVerificationRequestStatusUpdate

router = APIRouter(prefix="/employee", tags=["Employee"])

@router.get("/all-user-verifications", response_model=List[UserVerificationOut])
def get_all_user_verifications(db: Session = Depends(get_db)):
    user_verifications = db.query(UserVerification).filter(UserVerification.status == 'pending').all()
    print(user_verifications)
    return user_verifications

@router.get("/all-car-verifications", response_model=List[CarVerificationOut])
def get_all_car_verifications(db: Session = Depends(get_db)):
    car_verifications = db.query(CarVerification).filter(CarVerification.status == 'pending').all()
    return car_verifications


@router.post("/user-verification-update")
def update_verification_status(
    payload: UserVerificationStatusUpdate,
    db: Session = Depends(get_db)
):
    verification = db.query(UserVerification).filter(UserVerification.id == payload.verification_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Verification record not found")

    user = db.query(User).filter(User.id == verification.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")

    verification.status = payload.status
    verification.verifier_id = payload.verifier_id
    verification.updated_at = datetime.utcnow()

    user.verification_status = payload.status
    user.last_verified_id = verification.id

    if payload.status == "approved":
        # Update User's verified images
        user.license_photo_url = verification.license_photo_url
        user.passport_photo_url = verification.passport_photo_url
        user.rejection_reason = ""
    else:
        verification.rejection_reason = payload.rejection_reason
        user.rejection_reason = payload.rejection_reason

    db.commit()
    return {"message": f"User verification {payload.status}"}



@router.post("/car-verification-update")
def respond_to_car_request(payload: CarVerificationRequestStatusUpdate, db: Session = Depends(get_db)):
    # Get the verification record using the provided verification_id
    car_verification = db.query(CarVerification).filter(CarVerification.id == payload.verification_id).first()
    if not car_verification:
        raise HTTPException(status_code=404, detail="No verification found")

    # Now get the car from the verification record
    car = db.query(Car).filter(Car.id == car_verification.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="No car found for this verification")

    # Validate status
    if payload.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")

    # Update verification record
    car_verification.status = payload.status
    car_verification.rejection_reason = payload.rejection_reason
    car_verification.verifier_id = payload.verifier_id
    car_verification.updated_at = datetime.utcnow()

    # Update car verification status
    car.verification_status = payload.status
    car.rejection_reason = payload.rejection_reason
    car.last_verification_id = car_verification.id  # Optional, in case not already set
    car.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Car verification status updated successfully"}


