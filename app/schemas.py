from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Movie schemas
class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: int
    genre: str

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Showtime schemas
class ShowtimeBase(BaseModel):
    movie_id: int
    start_time: datetime
    total_seats: int

    @validator('total_seats')
    def validate_total_seats(cls, v):
        if v <= 0:
            raise ValueError('Total seats must be greater than 0')
        return v

class ShowtimeCreate(ShowtimeBase):
    pass

class Showtime(ShowtimeBase):
    id: int
    end_time: datetime
    available_seats: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Booking schemas
class BookingBase(BaseModel):
    showtime_id: int
    seats: int

    @validator('seats')
    def validate_seats(cls, v):
        if v <= 0:
            raise ValueError('Seats must be greater than 0')
        return v

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int
    status: str
    booking_time: datetime

    class Config:
        orm_mode = True

# Response schemas
class ShowtimeWithMovie(Showtime):
    movie: Movie

class BookingWithDetails(Booking):
    showtime: ShowtimeWithMovie