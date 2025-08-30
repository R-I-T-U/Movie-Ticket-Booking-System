import re
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timezone

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str

    @field_validator('username', 'full_name', mode='before')
    def validate_non_empty(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f'{field.name.capitalize()} cannot be empty')
        return v

class UserCreate(UserBase):
    password: str

    @field_validator('password', mode='before')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v


class User(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

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

    @field_validator('title', mode='before')
    def validate_title_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v
    
    @field_validator('genre', mode='before')
    def validate_genre_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Genre cannot be empty')
        return v

    @field_validator('description', mode='before')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty')
        return v

    @field_validator('duration', mode='before')
    def validate_duration(cls, v):
        if v < 5:
            raise ValueError('Movie duration must be at least 5 minutes')
        return v
    
class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Showtime schemas
class ShowtimeBase(BaseModel):
    movie_id: int
    start_time: datetime
    total_seats: int

    @field_validator('total_seats')
    def validate_total_seats(cls, v):
        if v <= 0:
            raise ValueError('Total seats must be greater than 0')
        return v

    @field_validator('start_time')
    def validate_start_time(cls, v):
        if v < datetime.now(timezone.utc):
            raise ValueError('Showtime time cannot be in the past')
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
        from_attributes = True

# Booking schemas
class BookingBase(BaseModel):
    showtime_id: int
    seats: int

    @field_validator('seats')
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
        from_attributes = True

# Response schemas
class ShowtimeWithMovie(Showtime):
    movie: Movie

class BookingWithDetails(Booking):
    showtime: ShowtimeWithMovie