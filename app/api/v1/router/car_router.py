from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.car_schema import CarVerificationRequest, CarSearchResponse, CarSearchRequest, CarOut, CarVerificationRequestStatusUpdate, CarVisibilityChangeRequest
from models.car_model import Car
from models.user_model import User
from models.car_verification_model import CarVerification
from database import get_db
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from typing import List, Optional
from math import radians, cos, sin, asin, sqrt

router = APIRouter(prefix="/car", tags=["Car"])


router = APIRouter()

def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


@router.post("/search-cars", response_model=List[CarSearchResponse])
def search_cars_optimized(search_params: CarSearchRequest, db: Session = Depends(get_db)):
    print(search_params)
    cars = db.query(Car).filter(
        Car.is_visible == True,
        # Car.verification_status == 'approved',
    ).all()
    available_cars = []
    for car in cars:
        distance = calculate_distance(
            search_params.latitude,
            search_params.longitude,
            car.latitude,
            car.longitude
        )
        if distance < search_params.distance:
            car_data = CarSearchResponse.from_orm(car)
            car_data.distance = distance
            available_cars.append(car_data)
    filtered_cars = available_cars

    if search_params.carType :
        filtered_cars = [car for car in filtered_cars if car.car_type == search_params.carType.lower()]
    
    if search_params.transmission:
        filtered_cars = [car for car in filtered_cars if car.transmission_type == search_params.transmission.lower()]

    if search_params.fuelType :
        filtered_cars = [car for car in filtered_cars if car.fuel_type == search_params.fuelType.lower()]

    if search_params.minRating:
        filtered_cars = [car for car in filtered_cars if car.car_rating >= search_params.minRating]

    # Apply sorting
    if search_params.sortBy == "nearest":
        filtered_cars.sort(key=lambda x: x.distance)
    elif search_params.sortBy == "price-low":
        filtered_cars.sort(key=lambda x: x.price_per_hour)
    elif search_params.sortBy == "price-high":
        filtered_cars.sort(key=lambda x: x.price_per_hour, reverse=True)

    return filtered_cars





@router.get("/car-details/{car_id}", response_model=CarOut)
def get_car_by_id(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


            
@router.get("/user-cars/{user_id}", response_model=List[CarOut])
def get_user_cars(user_id: int, db: Session = Depends(get_db)):
    print (user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cars = db.query(Car).filter(Car.owner_id == user_id).all()
    return cars


@router.post("/car-verification")
def create_or_update_car_request(payload: CarVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # If car_id is provided, search by car_id, otherwise we are creating a new car

    existing_car = None
    if payload.car_id:
        print("car_id provided")
        existing_car = db.query(Car).filter(Car.id == payload.car_id).first()

    def create_verification(car: Car):
        verification = CarVerification(
            car_id=car.id,
            car_number=payload.car_number,
            puc_image_url=payload.puc_image_url,
            puc_expiry_date=payload.puc_expiry_date,
            rc_image_url=payload.rc_image_url,
            rc_expiry_date=payload.rc_expiry_date,
            insurance_image_url=payload.insurance_image_url,
            insurance_expiry_date=payload.insurance_expiry_date,
            status='pending',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(verification)
        db.flush()  # Get verification.id before commit
        car.last_verification_id = verification.id
        car.verification_status = 'in_process'
        return verification

    if existing_car:
        # Check if verification-related fields changed
        needs_verification = (
            existing_car.car_number != payload.car_number or
            existing_car.puc_image_url != payload.puc_image_url or
            existing_car.puc_expiry_date != payload.puc_expiry_date or
            existing_car.rc_image_url != payload.rc_image_url or
            existing_car.rc_expiry_date != payload.rc_expiry_date or
            existing_car.insurance_image_url != payload.insurance_image_url or
            existing_car.insurance_expiry_date != payload.insurance_expiry_date or
            existing_car.verification_status in ['pending', 'rejected']
        )

        # Always update car info
        existing_car.company_name = payload.company_name
        existing_car.model_name = payload.model_name
        existing_car.manufacture_year = payload.manufacture_year
        existing_car.purchase_type = payload.purchase_type
        existing_car.ownership_count = payload.ownership_count
        existing_car.price_per_hour = payload.price_per_hour
        existing_car.location = payload.location
        existing_car.fuel_type = payload.fuel_type
        existing_car.features = payload.features
        existing_car.latitude = payload.latitude
        existing_car.longitude = payload.longitude
        existing_car.last_serviced_on = payload.last_serviced_on
        existing_car.future_booking_datetime = payload.future_booking_datetime
        existing_car.car_type = payload.car_type
        existing_car.transmission_type = payload.transmission_type
        existing_car.updated_at = datetime.utcnow()

        # Update car images
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

        # Update verification-related fields regardless
        existing_car.car_number = payload.car_number
        existing_car.puc_image_url = payload.puc_image_url
        existing_car.puc_expiry_date = payload.puc_expiry_date
        existing_car.rc_image_url = payload.rc_image_url
        existing_car.rc_expiry_date = payload.rc_expiry_date
        existing_car.insurance_image_url = payload.insurance_image_url
        existing_car.insurance_expiry_date = payload.insurance_expiry_date

        if needs_verification:
            print("Creating new verification")
            create_verification(existing_car)
            message = "Car updated and re-sent for verification"
        else:
            message = "Car updated without verification request"

        car_id = existing_car.id  # Return the car_id

    else:
        # Create new car
        new_car = Car(
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
            last_serviced_on=payload.last_serviced_on,
            features=payload.features,
            puc_image_url=payload.puc_image_url,
            puc_expiry_date=payload.puc_expiry_date,
            rc_image_url=payload.rc_image_url,
            rc_expiry_date=payload.rc_expiry_date,
            insurance_image_url=payload.insurance_image_url,
            insurance_expiry_date=payload.insurance_expiry_date,
            latitude=payload.latitude,
            longitude=payload.longitude,
            car_type=payload.car_type,
            transmission_type=payload.transmission_type,
            future_booking_datetime=payload.future_booking_datetime,            
            is_visible=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),

            # Car images
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

        db.add(new_car)
        db.flush()  # To get new_car.id
        create_verification(new_car)
        message = "New car added and sent for verification"
        car_id = new_car.id  # Return the car_id

    db.commit()
    return {"message": message, "car_id": car_id}


@router.post("/change-visibility")
def change_car_visibility(payload: CarVisibilityChangeRequest, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == payload.car_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found or unauthorized")

    car.is_visible = not car.is_visible
    car.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Car visibility updated to {car.is_visible}"}

@router.put("/cancel-car-verification/{car_id}")
def cancel_car_verification(car_id: int, db: Session = Depends(get_db)):
    # Retrieve the car by car_id
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Check if the car has an ongoing verification
    if not car.last_verification_id:
        raise HTTPException(status_code=404, detail="No verification found for this car")
    
    # Retrieve the verification record
    verification = db.query(CarVerification).filter(CarVerification.id == car.last_verification_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Car verification not found")
    
    # Update the verification status to 'canceled'
    verification.status = 'cancelled'
    verification.updated_at = datetime.utcnow()
    
    # Update the car's verification status to 'canceled'
    car.verification_status = 'pending'
    car.updated_at = datetime.utcnow()
    
    # Commit the changes to the database
    db.commit()

    return {"message": "Verification canceled successfully"}

