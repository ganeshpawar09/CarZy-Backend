from pydantic import BaseModel

class PostCarReview(BaseModel):
    user_id: int
    car_id: int
    booking_id: int
    rating: int
    review_text: str


