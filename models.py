from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Movie(BaseModel):
    title: str
    genre: str
    duration: int  # duration in minutes
    rating: float
    release_year: int

class Showtime(BaseModel):
    movie_id: str
    theater: str
    start_time: datetime
    end_time: datetime
    bookings: Optional[List[dict]] = []

class Booking(BaseModel):
    userId: str
    seat_number: int
    price: float
