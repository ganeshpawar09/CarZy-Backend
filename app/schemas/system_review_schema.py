from pydantic import BaseModel

class PostSystemReview(BaseModel):
    user_id: int
    rating: int
    description: str

