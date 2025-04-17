from fastapi import FastAPI
from database import engine
from api.v1.router import user_router 
from api.v1.router import otp_router
from api.v1.router import car_router
from fastapi.middleware.cors import CORSMiddleware
from models.base import Base

app = FastAPI()

# Add CORS middleware (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can limit this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables (this will create all tables defined in your models)
Base.metadata.create_all(bind=engine)

# Include the user-related routes
app.include_router(user_router.router, prefix="/api/v1", tags=["User"])
app.include_router(otp_router.router, prefix="/api/v1", tags=["Otp"])
app.include_router(car_router.router, prefix="/api/v1", tags=["Car"])

# You can add other routers for different modules like car, booking, etc.
# Example: app.include_router(car.router, prefix="/api/v1/car", tags=["car"])
