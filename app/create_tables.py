# create_tables.py
from database import engine
from models.base import Base
from models.user_model import User
from models.system_review_model import SystemReview
from models.car_model import Car
from models.car_verification_model import CarVerification
from models.user_verification_model import UserVerification
from models.otp_model import Otp

# import other models if needed

Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully.")
