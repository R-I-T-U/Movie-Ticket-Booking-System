from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.database import get_db
from app.auth import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/movies", response_model=List[schemas.Movie])
async def get_movies(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    movies = db.query(models.Movie).filter(models.Movie.is_active == True).offset(skip).limit(limit).all()
    return movies

@router.get("/movies/{movie_id}", response_model=schemas.Movie)
async def get_movie(
    movie_id: int, 
    db: Session = Depends(get_db)
):
    movie = db.query(models.Movie).filter(
        models.Movie.id == movie_id, 
        models.Movie.is_active == True
    ).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return movie

@router.get("/showtimes", response_model=List[schemas.ShowtimeWithMovie])
async def get_showtimes(
    movie_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Showtime).join(models.Movie).filter(
        models.Showtime.is_active == True,
        models.Movie.is_active == True
    )
    
    if movie_id:
        query = query.filter(models.Showtime.movie_id == movie_id)
    
    showtimes = query.offset(skip).limit(limit).all()
    return showtimes

@router.post("/bookings", response_model=schemas.Booking)
async def create_booking(
    booking: schemas.BookingCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if showtime exists and is active
    showtime = db.query(models.Showtime).filter(
        models.Showtime.id == booking.showtime_id,
        models.Showtime.is_active == True
    ).first()
    
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")
    
    # Check if there are enough seats available
    if showtime.available_seats < booking.seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")
    
    # Create booking
    db_booking = models.Booking(
        user_id=current_user.id,
        showtime_id=booking.showtime_id,
        seats=booking.seats
    )
    
    # Update available seats
    showtime.available_seats -= booking.seats
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking

@router.get("/bookings", response_model=List[schemas.BookingWithDetails])
async def get_user_bookings(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    bookings = db.query(models.Booking).filter(
        models.Booking.user_id == current_user.id
    ).all()
    
    return bookings

@router.delete("/bookings/{booking_id}")
async def cancel_booking(
    booking_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    
    # Update booking status
    booking.status = "cancelled"
    
    # Return seats to available seats
    showtime = db.query(models.Showtime).filter(
        models.Showtime.id == booking.showtime_id
    ).first()
    
    if showtime:
        showtime.available_seats += booking.seats
    
    db.commit()
    
    return {"message": "Booking cancelled successfully"}