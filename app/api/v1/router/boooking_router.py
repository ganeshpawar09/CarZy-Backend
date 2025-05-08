from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.payout_model import Payout
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

@router.get("/my-bookings/{user_id}", response_model=list[MyBookingOut])
def get_bookings_by_user(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    return bookings

@router.get("/my-car-bookings/{user_id}", response_model=list[MyCarBookingOut])
def get_my_car_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.car_owner_id == user_id).all()
    return bookings

@router.get("/coupon/{coupon_id}", response_model=float)
def get_coupon_discount(coupon_id: int, db: Session = Depends(get_db)):
    coupon = db.query(Coupon).filter(
        Coupon.id == coupon_id,
        Coupon.used == False  
    ).first()

    if not coupon:
        return -1.0 
    
    return coupon.discount

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
    car = db.query(Car).filter(Car.id == payload.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    pickup_otp = generate_otp()
    drop_otp = generate_otp()

    if payload.coupon_id:
        coupon = db.query(Coupon).filter(Coupon.id == payload.coupon_id, Coupon.used == False).first()
        if not coupon:
            raise HTTPException(status_code=400, detail="Invalid or already used coupon")
        coupon.used = True


 
    # Verify payment status
    payment_status = "pending"
    if payload.razorpay_payment_id:
        try:
            razorpay_payment = razorpay_client.payment.fetch(payload.razorpay_payment_id)
            if razorpay_payment['status'] == 'captured':
                payment_status = 'paid'
            else:
                payment_status = razorpay_payment['status']
        except Exception as e:
            print(f"Razorpay fetch error: {str(e)}")

    payment = Payment(
        booking_id=None, 
        user_id=payload.user_id,
        total_hours=payload.total_hours,
        price_per_hour=payload.price_per_hour,
        
        security_deposit=payload.security_deposit,
        coupon_discount=payload.coupon_discount or 0.0,
        status=payment_status,
        razorpay_payment_id=payload.razorpay_payment_id,
        created_at=datetime.utcnow()
    )
    db.add(payment)
    db.flush()

    booking = Booking(
        user_id=payload.user_id,
        car_id=payload.car_id,
        car_owner_id=payload.car_owner_id,
        start_datetime=payload.start_datetime,
        end_datetime=payload.end_datetime,
        pickup_delivery_location=payload.pickup_delivery_location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status='booked',
        pickup_otp=pickup_otp,
        drop_otp=drop_otp,
        payment_id=payment.id,
        total_hours=payload.total_hours,
        price_per_hour=payload.price_per_hour,
        security_deposit=payload.security_deposit,
        coupon_discount=payload.coupon_discount or 0.0,
        created_at=datetime.utcnow()
    )
    db.add(booking)
    db.flush()

    payment.booking_id = booking.id

    new_booking_range = f"{payload.start_datetime.isoformat()} to {payload.end_datetime.isoformat()}"
    car.future_booking_datetime = (car.future_booking_datetime + " | " + new_booking_range) if car.future_booking_datetime else new_booking_range

    db.commit()

    return {
        "message": "Booking successful",
    }



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

    # Save after-drop images
    booking.after_front_image_url = data.after_front_image_url or booking.after_front_image_url
    booking.after_rear_image_url = data.after_rear_image_url or booking.after_rear_image_url
    booking.after_left_side_image_url = data.after_left_side_image_url or booking.after_left_side_image_url
    booking.after_right_side_image_url = data.after_right_side_image_url or booking.after_right_side_image_url

    # Update car's future_booking_datetime
    car = db.query(Car).filter(Car.id == booking.car_id).first()
    time_range = f"{booking.start_datetime} to {booking.end_datetime}"
    if car and car.future_booking_datetime:
        slots = car.future_booking_datetime.split(" | ")
        car.future_booking_datetime = " | ".join([s for s in slots if s.strip() != time_range])

    # Handle refund, late fee, penalty
    payment = db.query(Payment).filter(Payment.id == booking.payment_id).first()
    late_charge  = 0
    refund_amount = 0
    deduction_reason = None
    penalty_reason = None

    grace_period_end = booking.end_datetime + timedelta(hours=1)
    if now > grace_period_end:
        late_hours = (now - grace_period_end).total_seconds() / 3600
        late_hours_rounded = round(late_hours + 0.5)  # Round to nearest hour
        late_charge  = int(payment.price_per_hour * late_hours_rounded)

        if late_charge  <= payment.security_deposit:
            refund_amount = payment.security_deposit - late_charge 
            deduction_reason = f"Late return by {late_hours_rounded} hours"
        else:
            penalty_amount = late_charge  - payment.security_deposit
            refund_amount = 0
            deduction_reason = f"Security fully deducted. Late by {late_hours_rounded} hours"
            penalty_reason = f"Late return by {late_hours_rounded} hours"
            
            
            penalty = Penalty(
            user_id=booking.car_owner_id,
            booking_id=booking.id,
            penalty_amount=penalty_amount,
            penalty_reason=penalty_reason,
            reason="late_drop",
            payment_status="unpaid"
    )
            db.add(penalty)
    else:
        refund_amount = payment.security_deposit

    booking.late_charge = late_charge
    # Create refund
    refund = Refund(
        user_id=booking.user_id,
        booking_id=booking.id,
        reason="refundable",
        deduction_amount=late_charge  if late_charge  > 0 else 0,
        deduction_reason=deduction_reason,
        refund_amount=refund_amount
    )
    db.add(refund)

    db.commit()

    base_rent = booking.total_hours * booking.price_per_hour
    coupon_discount_amount = round(base_rent * (booking.coupon_discount or 0) / 100)
    earning_before_payout = booking.late_charge + base_rent - coupon_discount_amount

    # Compute final payout: 90% of the above
    payout_amount = 0.9 * earning_before_payout

    # Create Payout entry
    payout = Payout(
        owner_id=booking.car_owner_id,
        booking_id=booking.id,
        car_id=booking.car_id,
        total_hours=booking.total_hours,
        price_per_hour=booking.price_per_hour,
        coupon_discount=booking.coupon_discount or 0,
        late_charge=booking.late_charge or 0,
        payout_amount=payout_amount,
        status='pending',
    )

    db.add(payout)
    db.commit()

    return {"message": "Drop confirmed successfully"}


@router.post("/cancel-by-owner")
def cancel_by_owner(data: BookingCancellationByOwner, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(
        Booking.id == data.booking_id,
        Booking.car_owner_id == data.owner_id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not owned by this owner")

    payment = db.query(Payment).filter(Payment.id == booking.payment_id).first()
    if not payment:
        raise HTTPException(status_code=500, detail="Payment record not found")

    # Calculate values
    penalty_amount = 0.1 *(round(payment.total_hours * payment.price_per_hour) -(round(payment.total_hours * payment.price_per_hour)*payment.coupon_discount/100) )# 10% of booking amount
    refund_amount = round(payment.total_hours * payment.price_per_hour)-(round(payment.total_hours * payment.price_per_hour)*payment.coupon_discount/100) + payment.security_deposit  # Full refund

    # Update booking
    booking.status = "cancelled_by_owner"

    # Remove slot from car’s future bookings
    car = db.query(Car).filter(Car.id == booking.car_id).first()
    time_range = f"{booking.start_datetime} to {booking.end_datetime}"
    if car and car.future_booking_datetime:
        slots = car.future_booking_datetime.split(" | ")
        car.future_booking_datetime = " | ".join([s for s in slots if s.strip() != time_range])

    # Create refund with detailed reason
    refund = Refund(
        user_id=booking.user_id,
        booking_id=booking.id,
        reason="cancelled_by_owner",
        deduction_amount=0,
        deduction_reason="No deductions — full refund due to owner's cancellation",
        refund_amount=refund_amount
    )
    db.add(refund)

    # Create penalty with detailed reason
    penalty = Penalty(
        user_id=booking.car_owner_id,
        booking_id=booking.id,
        penalty_amount=penalty_amount,
        penalty_reason="Penalty charged because owner cancelled the booking before trip start",
        reason="cancelled_by_owner",
        payment_status="unpaid"
    )
    db.add(penalty)

    # Optional: Give user a coupon
    coupon = Coupon(
        user_id=booking.user_id,
        discount=10.0,
    )
    db.add(coupon)

    db.commit()

    return {"message": "Booking cancelled successfully by owner"}


from datetime import datetime

@router.post("/cancel")
def cancel_booking(data: BookingCancellation, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != data.user_id:
        raise HTTPException(status_code=403, detail="You can only cancel your own booking")

    if booking.status in ["cancelled", "cancelled_by_owner", "completed"]:
        raise HTTPException(status_code=400, detail=f"Booking already {booking.status.replace('_', ' ')}")

    now = datetime.utcnow()
    if now >= booking.start_datetime:
        raise HTTPException(status_code=400, detail="Cannot cancel after booking start time")

    payment = db.query(Payment).filter(Payment.id == booking.payment_id).first()
    if not payment:
        raise HTTPException(status_code=500, detail="Payment not found")

   
    refund_percentage = max(0,data.refund_percentage) 

    refundable_amount = round((round(payment.total_hours * payment.price_per_hour) -(round(payment.total_hours * payment.price_per_hour)*payment.coupon_discount/100) ) * (refund_percentage / 100), 2)
    deduction_amount = round((round(payment.total_hours * payment.price_per_hour) -(round(payment.total_hours * payment.price_per_hour)*payment.coupon_discount/100) ) - refundable_amount, 2)
    total_refund = refundable_amount + payment.security_deposit

    # Update booking status
    booking.status = 'cancelled_by_user'

    # Create refund record
    refund = Refund(
        user_id=booking.user_id,
        booking_id=booking.id,
        reason="cancelled_by_user",
        refund_amount=total_refund,
        deduction_amount=deduction_amount,
        deduction_reason=f"{round(refund_percentage)}% refund based on remaining time before start"
    )
    db.add(refund)

    # Remove time range from future_booking_datetime
    car = db.query(Car).filter(Car.id == booking.car_id).first()
    if car and car.future_booking_datetime:
        time_range = f"{booking.start_datetime} - {booking.end_datetime}"
        slots = car.future_booking_datetime.split(" | ")
        car.future_booking_datetime = " | ".join([s for s in slots if s.strip() != time_range])

    db.commit()

    return {"message": "Booking cancelled"}
