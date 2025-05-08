from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from models.payout_model import Payout
from database import get_db
from models.user_model import User
from models.car_model import Car
from models.booking_model import Booking
from models.payment_model import Payment
from models.refund_model import Refund
from models.penalty_model import Penalty
from models.coupon_model import Coupon
from models.car_review_model import CarReview
from models.system_review_model import SystemReview
from models.otp_model import Otp

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/")
def get_dashboard_data(db: Session = Depends(get_db)):
    # USERS
    total_users = db.query(User).count()
    total_verified_users = db.query(User).filter(User.verification_status == 'approved', User.user_type == 'user').count()
    total_owners = db.query(User).filter(User.user_type == 'owner').count()
    total_employees = db.query(User).filter(User.user_type == 'employee').count()

    # USER GROWTH (Last 6 months) - count both users and owners as "users"
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    user_growth = (
        db.query(
            extract('year', User.created_at).label('year'),
            extract('month', User.created_at).label('month'),
            func.count(User.id)
        )
        .filter(User.created_at >= six_months_ago, User.user_type.in_(['user', 'owner']))
        .group_by('year', 'month')
        .order_by('year', 'month')
        .all()
    )
    user_growth_data = [
        {"month": f"{int(y)}-{int(m):02d}", "count": c} for y, m, c in user_growth
    ]

    # CARS
    total_cars = db.query(Car).count()
    verified_cars = db.query(Car).filter(Car.verification_status == 'approved').count()

    cars_by_fuel_type = dict(
        db.query(Car.fuel_type, func.count(Car.id)).group_by(Car.fuel_type).all()
    )
    cars_by_transmission = dict(
        db.query(Car.transmission_type, func.count(Car.id)).group_by(Car.transmission_type).all()
    )
    cars_by_type = dict(
        db.query(Car.car_type, func.count(Car.id)).group_by(Car.car_type).all()
    )

    # BOOKINGS
    total_bookings = db.query(Booking).count()

    booking_status_counts = dict(
        db.query(Booking.status, func.count(Booking.id)).group_by(Booking.status).all()
    )

    total_booking_time = db.query(func.sum(Booking.total_hours)).scalar() or 0
    average_booking_time = db.query(func.avg(Booking.total_hours)).scalar() or 0

    total_booking_amount = db.query(
        func.sum(
            (Booking.total_hours * Booking.price_per_hour) - 
            ((Booking.total_hours * Booking.price_per_hour * Booking.coupon_discount) / 100) + 
            Booking.late_charge
        )
    ).scalar() or 0

    average_booking_amount = db.query(
        func.avg(
            (Booking.total_hours * Booking.price_per_hour) - 
            ((Booking.total_hours * Booking.price_per_hour * Booking.coupon_discount) / 100) + 
            Booking.late_charge
        )
    ).scalar() or 0

    # REVIEWS
    rating_counts = dict(
        db.query(SystemReview.rating, func.count(SystemReview.id))
        .group_by(SystemReview.rating)
        .all()
    )
    reviews = {
        "five_star": rating_counts.get(5, 0),
        "four_star": rating_counts.get(4, 0),
        "three_star": rating_counts.get(3, 0),
        "two_star": rating_counts.get(2, 0),
        "one_star": rating_counts.get(1, 0),
    }

    # FINANCIALS
    total_transaction_amount = db.query(
        func.sum(
            (Payment.total_hours * Payment.price_per_hour) - 
            ((Payment.total_hours * Payment.price_per_hour * Payment.coupon_discount) / 100) 
            
        )
    ).scalar() or 0

    refunded_amount = db.query(func.sum(Refund.refund_amount)).scalar() or 0
    penalty_amount = db.query(func.sum(Penalty.penalty_amount)).scalar() or 0

    payouts = db.query(Payout).all()
    total_payout = sum(payout.payout_amount for payout in payouts)

    coupons_given = db.query(Coupon).count()

    # FINAL DATA
    return {
        "users": {
            "total_users": total_users,
            "total_verified_users": total_verified_users,
            "total_owners": total_owners,
            "total_employees": total_employees,
            "user_growth_last_six_months": user_growth_data
        },
        "cars": {
            "total_cars": total_cars,
            "verified_cars": verified_cars,
            "cars_by_fuel_type": cars_by_fuel_type,
            "cars_by_transmission": cars_by_transmission,
            "cars_by_type": cars_by_type
        },
        "bookings": {
            "total_bookings": total_bookings,
            "status_counts": booking_status_counts,
            "total_booking_time_hours": total_booking_time,
            "average_booking_time_hours": average_booking_time,
            "total_booking_amount": total_booking_amount,
            "average_booking_amount": average_booking_amount
        },
        "reviews": reviews,
        "financials": {
            "total_transaction_amount": total_transaction_amount,
            "refunded_amount": refunded_amount,
            "penalty_amount": penalty_amount,
            "coupons_given": coupons_given,
            "total_payout": total_payout
        }
    }
