from sqlalchemy import Column, Integer, Float, DateTime, Enum, ForeignKey, Text
from datetime import datetime
from models.base import Base

class Refund(Base):
    __tablename__ = 'refund'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)              # Who receives the refund
    booking_id = Column(Integer, ForeignKey('booking.id'), nullable=False)

    user_payment_id = Column(Integer, ForeignKey('payment.id'), nullable=False)   # Payment made by the user
    refund_payment_id = Column(Integer, ForeignKey('payment.id'), nullable=True)  # Payment returned to user

    status = Column(
        Enum('in_process', 'approved', 'rejected', 'opposed', 'completed'),
        default='in_process',
        nullable=False
    )
    reason = Column(
        Enum('cancellation', 'refundable', 'cancelled_by_owner'),
        nullable=False
    )

    deduction_amount = Column(Float, default=0)
    deduction_reason = Column(Text, nullable=True)
    refund_amount = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
