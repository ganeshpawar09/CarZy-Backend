from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.car_schema import CarVerificationRequest, CarVerificationRequestStatusUpdate, CarVisibilityChangeRequest
from models.car_model import Car
from models.user_model import User
from database import get_db
from datetime import datetime

router = APIRouter(prefix="/car", tags=["Car"])

@router.post("/car-verification")
def create_or_update_car_request(payload: CarVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_car = db.query(Car).filter(Car.car_number == payload.car_number).first()

    if existing_car:
        # Update existing car
        existing_car.company_name = payload.company_name
        existing_car.model_name = payload.model_name
        existing_car.manufacture_year = payload.manufacture_year
        existing_car.purchase_type = payload.purchase_type
        existing_car.ownership_count = payload.ownership_count
        existing_car.price_per_hour = payload.price_per_hour
        existing_car.location = payload.location
        existing_car.fuel_type = payload.fuel_type
        existing_car.features = payload.features
        existing_car.puc_image_url = payload.puc_image_url
        existing_car.puc_expiry_date = payload.puc_expiry_date
        existing_car.rc_image_url = payload.rc_image_url
        existing_car.rc_expiry_date = payload.rc_expiry_date
        existing_car.insurance_image_url = payload.insurance_image_url
        existing_car.insurance_expiry_date = payload.insurance_expiry_date
        existing_car.latitude = payload.latitude
        existing_car.longitude = payload.longitude

        # Newly added individual image fields
        existing_car.front_view_image_url = payload.front_view_image_url
        existing_car.rear_view_image_url = payload.rear_view_image_url
        existing_car.left_side_image_url = payload.left_side_image_url
        existing_car.right_side_image_url = payload.right_side_image_url
        existing_car.diagonal_front_left_image_url = payload.diagonal_front_left_image_url
        existing_car.diagonal_rear_right_image_url = payload.diagonal_rear_right_image_url
        existing_car.dashboard_image_url = payload.dashboard_image_url
        existing_car.speedometer_fuel_gauge_image_url = payload.speedometer_fuel_gauge_image_url
        existing_car.front_seats_image_url = payload.front_seats_image_url
        existing_car.rear_seats_image_url = payload.rear_seats_image_url
        existing_car.boot_space_image_url = payload.boot_space_image_url
        existing_car.tyre_condition_image_url = payload.tyre_condition_image_url

        existing_car.verification_status = "in_process"
        existing_car.updated_at = datetime.utcnow()
        message = "Car details updated and sent for verification"
    else:
        # Create new car
        new_request = Car(
            owner_id=payload.owner_id,
            company_name=payload.company_name,
            model_name=payload.model_name,
            car_number=payload.car_number,
            manufacture_year=payload.manufacture_year,
            purchase_type=payload.purchase_type,
            ownership_count=payload.ownership_count,
            price_per_hour=payload.price_per_hour,
            location=payload.location,
            fuel_type=payload.fuel_type,
            features=payload.features,
            puc_image_url=payload.puc_image_url,
            puc_expiry_date=payload.puc_expiry_date,
            rc_image_url=payload.rc_image_url,
            rc_expiry_date=payload.rc_expiry_date,
            insurance_image_url=payload.insurance_image_url,
            insurance_expiry_date=payload.insurance_expiry_date,
            latitude=payload.latitude,
            longitude=payload.longitude,
            is_visible=True,
            verification_status="in_process",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),

            # Newly added image fields
            front_view_image_url=payload.front_view_image_url,
            rear_view_image_url=payload.rear_view_image_url,
            left_side_image_url=payload.left_side_image_url,
            right_side_image_url=payload.right_side_image_url,
            diagonal_front_left_image_url=payload.diagonal_front_left_image_url,
            diagonal_rear_right_image_url=payload.diagonal_rear_right_image_url,
            dashboard_image_url=payload.dashboard_image_url,
            speedometer_fuel_gauge_image_url=payload.speedometer_fuel_gauge_image_url,
            front_seats_image_url=payload.front_seats_image_url,
            rear_seats_image_url=payload.rear_seats_image_url,
            boot_space_image_url=payload.boot_space_image_url,
            tyre_condition_image_url=payload.tyre_condition_image_url,
        )
        db.add(new_request)
        message = "Car sent for verification"

    db.commit()
    return {"message": message}


@router.post("/car-verification-update")
def respond_to_car_request(payload: CarVerificationRequestStatusUpdate, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == payload.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="No car found")

    if payload.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")

    car.verification_status = payload.status
    car.rejection_reason = payload.rejection_reason
    car.last_verified_by = payload.verified_by
    car.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Car verification updated"}


@router.post("/change-visibility")
def change_car_visibility(payload: CarVisibilityChangeRequest, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == payload.car_id, Car.owner_id == payload.owner_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found or unauthorized")

    car.is_visible = payload.is_visible
    car.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Car visibility updated to {payload.is_visible}"}
