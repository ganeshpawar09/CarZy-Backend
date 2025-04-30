from fastapi import FastAPI
from database import engine
from api.v1.router import user_router 
from api.v1.router import otp_router
from api.v1.router import car_router
from api.v1.router import boooking_router
from api.v1.router import employee_router
from api.v1.router import admin_router
from fastapi.middleware.cors import CORSMiddleware
from models.base import Base

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(user_router.router, prefix="/api/v1", tags=["User"])
app.include_router(otp_router.router, prefix="/api/v1", tags=["Otp"])
app.include_router(car_router.router, prefix="/api/v1", tags=["Car"])
app.include_router(boooking_router.router, prefix="/api/v1", tags=["Booking"])
app.include_router(employee_router.router, prefix="/api/v1", tags=["Employee"])
app.include_router(admin_router.router, prefix="/api/v1", tags=["Admin"])
