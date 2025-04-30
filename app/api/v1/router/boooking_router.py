from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.booking_model import Booking
from models.payment_model import Payment
from models.coupon_model import Coupon
from models.refund_model import Refund
from models.penalty_model import Penalty
from database import get_db
from schemas.booking_schema import RazorpayOrderRequest,PaymentVerificationRequest, BookingCancellation, BookingRequest, MyBookingOut, MyCarBookingOut, PickupConfirmation, DropConfirmation, BookingCancellationByOwner
from datetime import datetime, timedelta
from models.car_model import Car
import random
import os
import razorpay
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/booking", tags=["Booking"])


def generate_otp():
    return str(random.randint(1000, 9999))

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)

@router.post("/create-razorpay-order")
def create_razorpay_order(payload: RazorpayOrderRequest):
    try:
        # Create Razorpay order
        order_data = {
            "amount": int(payload.amount),  # Amount should be in paise
            "currency": payload.currency,
            "receipt": payload.receipt,
            "notes": payload.notes or {}
        }
        
        order = razorpay_client.order.create(data=order_data)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Razorpay order: {str(e)}")

@router.post("/verify-payment")
def verify_payment(payload: PaymentVerificationRequest):
    try:
        # Generate signature verification data
        generated_signature = hmac.new(
            bytes(RAZORPAY_KEY_SECRET, "utf-8"),
            (payload.razorpay_order_id + "|" + payload.razorpay_payment_id).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        is_signature_valid = hmac.compare_digest(
            generated_signature,
            payload.razorpay_signature
        )
        
        if not is_signature_valid:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Fetch payment details from Razorpay
        payment = razorpay_client.payment.fetch(payload.razorpay_payment_id)
        
        # Check if payment was successful
        if payment['status'] != 'captured':
            raise HTTPException(status_code=400, detail=f"Payment not successful. Status: {payment['status']}")
        
        return {"status": "success", "payment_id": payload.razorpay_payment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")

@router.post("/booking")
def create_booking(payload: BookingRequest, db: Session = Depends(get_db)):
        # Check if car exists
        car = db.query(Car).filter(Car.id == payload.car_id).first()
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")

        # Generate OTPs for pickup and drop
        pickup_otp = generate_otp()
        drop_otp = generate_otp()
        
        # Handle coupon if provided
        if payload.coupon_id:
            coupon = db.query(Coupon).filter(
                Coupon.id == payload.coupon_id,
                Coupon.used == False
            ).first()
            if not coupon:
                raise HTTPException(status_code=400, detail="Invalid or already used coupon")
            coupon.used = True

        # Verify Razorpay payment
        payment_status = 'pending'
        if payload.razorpay_payment_id:
            try:
                # Fetch payment details from Razorpay
                razorpay_payment = razorpay_client.payment.fetch(payload.razorpay_payment_id)
                
                # Check payment status
                if razorpay_payment['status'] == 'captured':
                    payment_status = 'paid'
                else:
                    payment_status = razorpay_payment['status']
            except Exception as e:
                print(f"Error fetching Razorpay payment: {str(e)}")
                # Continue with booking creation but mark payment as pending

        # Create payment record
        payment = Payment(
            booking_id=None,
            user_id=payload.user_id,
            total_hours=payload.total_hours,
            price_per_hour=payload.price_per_hour,
            total_amount=payload.total_amount,
            security_deposit=payload.security_deposit,
            coupon_discount=payload.coupon_discount,
            status=payment_status,
            created_at=datetime.utcnow()
        )
        db.add(payment)
        db.flush()  # Get the payment ID

        # Create booking record
        booking = Booking(
            user_id=payload.user_id,
            car_id=payload.car_id,
            car_owner_id=payload.car_owner_id,
            start_datetime=payload.start_datetime,
            end_datetime=payload.end_datetime,
            pickup_delivery_location=payload.pickup_delivery_location,
            latitude=payload.latitude,
            longitude=payload.longitude,
            status='booked' if payment_status == 'paid' else 'payment_pending',
            total_hours=payload.total_hours,
            price_per_hour=payload.price_per_hour,
            total_amount=payload.total_amount,
            security_deposit=payload.security_deposit,
            coupon_discount=payload.coupon_discount,
            pickup_otp=pickup_otp,
            drop_otp=drop_otp,
            payment_id=payment.id,
            created_at=datetime.utcnow()
        )
        db.add(booking)
        db.flush()  # Get the booking ID

        # Update payment with booking ID
        payment.booking_id = booking.id

        # Update car's future booking dates
        new_booking_time = f"{payload.start_datetime} - {payload.end_datetime}"
        if car.future_booking_datetime:
            car.future_booking_datetime += f" | {new_booking_time}"
        else:
            car.future_booking_datetime = new_booking_time

        db.commit()
        
        return {
            "message": "Booking successful", 
            "booking_id": booking.id,
            "payment_status": payment_status
        }
   
@router.get("/my-bookings/{user_id}", response_model=list[MyBookingOut])
def get_bookings_by_user(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user")
    return bookings

@router.get("/my-car-bookings/{user_id}", response_model=list[MyCarBookingOut])
def get_my_car_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.car_owner_id == user_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for your cars")
    return bookings


@router.post("/pickup")
def confirm_pickup(data: PickupConfirmation, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.pickup_otp_used:
        raise HTTPException(status_code=400, detail="Pickup already confirmed")

    if booking.pickup_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Update pickup status
    booking.status = 'picked'
    booking.pickup_otp_used = True
    booking.picked_time = datetime.utcnow()

    # Optional image fields
    if data.before_front_image_url:
        booking.before_front_image_url = data.before_front_image_url
    if data.before_rear_image_url:
        booking.before_rear_image_url = data.before_rear_image_url
    if data.before_left_side_image_url:
        booking.before_left_side_image_url = data.before_left_side_image_url
    if data.before_right_side_image_url:
        booking.before_right_side_image_url = data.before_right_side_image_url
    if data.before_interior_image_url:
        booking.before_interior_image_url = data.before_interior_image_url

    db.commit()

    return {"message": "Pickup confirmed successfully"}




@router.post("/drop")
def confirm_drop(data: DropConfirmation, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.drop_otp_used:
        raise HTTPException(status_code=400, detail="Drop already confirmed")

    if booking.drop_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    now = datetime.utcnow()
    booking.status = "completed"
    booking.drop_otp_used = True
    booking.returned_time = now

    # Optional after-drop photos
    booking.after_front_image_url = data.after_front_image_url or booking.after_front_image_url
    booking.after_rear_image_url = data.after_rear_image_url or booking.after_rear_image_url
    booking.after_left_side_image_url = data.after_left_side_image_url or booking.after_left_side_image_url
    booking.after_right_side_image_url = data.after_right_side_image_url or booking.after_right_side_image_url
    booking.after_interior_image_url = data.after_interior_image_url or booking.after_interior_image_url

    # Remove from car's future booking slot
    car = db.query(Car).filter(Car.id == booking.car_id).first()
    time_range = f"{booking.start_datetime} - {booking.end_datetime}"
    if car and car.future_booking_datetime:
        slots = car.future_booking_datetime.split(" | ")
        car.future_booking_datetime = " | ".join([s for s in slots if s.strip() != time_range])

    # Late fee logic
    late_fee = 0
    refund_amount = 0

    if now > booking.end_datetime + timedelta(hours=1):
        late_hours = (now - (booking.end_datetime + timedelta(hours=1))).total_seconds() / 3600
        late_fee = int(booking.price_per_hour * late_hours)
        booking.late_charged = late_fee

        if late_fee <= booking.security_deposit:
            refund_amount = booking.security_deposit - late_fee
        else:
            refund_amount = 0
            penalty_amount = late_fee - booking.security_deposit
            penalty = Penalty(
                user_id=booking.user_id,
                booking_id=booking.id,
                amount=penalty_amount,
                reason='late_return'
            )
            db.add(penalty)
    else:
        refund_amount = booking.security_deposit - booking.late_charged
    
    # Create refund
    refund = Refund(
        user_id=booking.user_id,
        booking_id=booking.id,
        reason='refundable',
        deduction_amount=late_fee,
        deduction_reason="Late drop-off" if late_fee > 0 else None,
        refund_amount=refund_amount
    )

    db.add(refund)
    db.flush()

    booking.refund_id = refund.id
    db.commit()

    return {
        "message": "Drop confirmed successfully",
    }


@router.post("/cancel-by-owner")
def cancel_by_owner(data: BookingCancellationByOwner, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == data.booking_id, Booking.car_owner_id == data.owner_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not owned by this owner")
    if booking.status == "cancelled_by_owner":
        raise HTTPException(status_code=400, detail="Booking already cancelled by owner")
    # Calculate 10% penalty for the owner
    penalty_amount = 0.1 * booking.total_amount  # 10% of the total booking amount
    # Refund the full amount to the user
    refund_amount = booking.total_amount
    # Update the booking status to "cancelled_by_owner"
    booking.status = "cancelled_by_owner"
    db.commit()
    # Remove the booking time from the car's future bookings
    car = db.query(Car).filter(Car.id == booking.car_id).first()
    time_range = f"{booking.start_datetime} - {booking.end_datetime}"
    if car and car.future_booking_datetime:
        slots = car.future_booking_datetime.split(" | ")
        car.future_booking_datetime = " | ".join([s for s in slots if s.strip() != time_range])
    db.commit()
    # Create a refund record for the user
    refund = Refund(
        user_id=booking.user_id,
        booking_id=booking.id,
        reason='cancelled_by_owner',
        deduction_amount=0,  # No deductions, the user gets the full refund
        refund_amount=refund_amount
    )
    db.add(refund)
    db.flush()
    # Link the refund to the booking
    booking.refund_id = refund.id
    db.commit()
    # Add penalty record for the owner
    penalty = Penalty(
        user_id=booking.car_owner_id,
        booking_id=booking.id,
        amount=penalty_amount,
        reason='cancelled_by_owner'
    )
    db.add(penalty)

    coupon = Coupon(
        user_id=booking.user_id,
        discount_percentage=10.0,
        issued_for_reason="owner cancelled trip"
    )
    db.add(coupon)

    db.commit()

    db.commit()
    return {
        "message": "Booking cancelled successfully by owner"    }


@router.post("/cancel")
def cancel_booking(data: BookingCancellation, db: Session = Depends(get_db)):
    # Retrieve the booking
    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check if the user trying to cancel is the one who made the booking
    if booking.user_id != data.user_id:
        raise HTTPException(status_code=403, detail="You can only cancel your own booking")

    # Mark the booking as cancelled
    booking.status = 'cancelled'
    
    # Calculate the main amount (total amount - security deposit)
    main_amount = booking.total_amount - booking.security_deposit
    
    # Apply coupon discount to the main amount
    if booking.coupon_discount:
        main_amount -= (main_amount * booking.coupon_discount)

    # Calculate the refundable amount based on the percentage input
    refundable_amount = main_amount * (data.refund_percentage / 100)

    # Deduct the remaining amount
    deduction_amount = main_amount - refundable_amount

    # Create refund record
    refund = Refund(
        user_id=booking.user_id,
        booking_id=booking.id,
        reason='cancellation',
        deduction_amount=deduction_amount,
        refund_amount=refundable_amount,
        deduction_reason="Booking cancelled"
    )
    db.add(refund)
    db.flush()

    # Assign the refund ID to the booking
    booking.refund_id = refund.id
    db.commit()

    # Remove the booking time from the car's future booking list
    car = db.query(Car).filter(Car.id == booking.car_id).first()
    if car and car.future_booking_datetime:
        time_range = f"{booking.start_datetime} - {booking.end_datetime}"
        slots = car.future_booking_datetime.split(" | ")
        car.future_booking_datetime = " | ".join([s for s in slots if s.strip() != time_range])

    db.commit()

    return {"message": "Booking cancelled successfully. Refund processed."}