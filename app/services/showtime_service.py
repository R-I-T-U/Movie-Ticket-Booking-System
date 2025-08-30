from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from datetime import timedelta
from app import models, schemas

def create_showtime(showtime_data: schemas.ShowtimeCreate, db: Session):
    movie = db.query(models.Movie).filter(
        models.Movie.id == showtime_data.movie_id,
        models.Movie.is_active == True
    ).first()
    
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    end_time = showtime_data.start_time + timedelta(minutes=movie.duration)
    
    # Add buffer time (20 minutes before and after)
    buffer_before = timedelta(minutes=20)
    buffer_after = timedelta(minutes=20)
    
    # Check for overlapping showtimes in the same cinema hall
    # Consider buffer time for cleaning and preparation
    overlapping_showtime = db.query(models.Showtime).filter(
        models.Showtime.cinema_hall_id == showtime_data.cinema_hall_id,
        or_(
            # New showtime starts during existing showtime (with buffer)
            and_(
                showtime_data.start_time >= models.Showtime.start_time - buffer_before,
                showtime_data.start_time < models.Showtime.end_time + buffer_after
            ),
            # New showtime ends during existing showtime (with buffer)
            and_(
                end_time > models.Showtime.start_time - buffer_before,
                end_time <= models.Showtime.end_time + buffer_after
            ),
            # New showtime completely contains existing showtime
            and_(
                showtime_data.start_time <= models.Showtime.start_time - buffer_before,
                end_time >= models.Showtime.end_time + buffer_after
            )
        )
    ).first()
    
    if overlapping_showtime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cinema hall is already occupied from {overlapping_showtime.start_time} to {overlapping_showtime.end_time}"
        )
    
    # Create the showtime
    db_showtime = models.Showtime(
        **showtime_data.model_dump(),
        end_time=end_time,
        available_seats=showtime_data.total_seats
    )
    
    db.add(db_showtime)
    db.commit()
    db.refresh(db_showtime)
    return db_showtime

def update_showtime(showtime_id: int, showtime_data: schemas.ShowtimeCreate, db: Session):
    db_showtime = db.query(models.Showtime).filter(models.Showtime.id == showtime_id).first()
    
    if not db_showtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")
    
    movie = db.query(models.Movie).filter(
        models.Movie.id == showtime_data.movie_id,
        models.Movie.is_active == True
    ).first()
    
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    end_time = showtime_data.start_time + timedelta(minutes=movie.duration)
    
    if showtime_data.total_seats != db_showtime.total_seats:
        seats_diff = showtime_data.total_seats - db_showtime.total_seats
        db_showtime.available_seats += seats_diff
    
    for key, value in showtime_data.model_dump().items():
        if key != 'total_seats':
            setattr(db_showtime, key, value)
    
    db_showtime.end_time = end_time
    db.commit()
    db.refresh(db_showtime)
    return db_showtime 

def get_showtimes(db: Session, movie_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Showtime).join(models.Movie).filter(
        models.Showtime.is_active == True,
        models.Movie.is_active == True
    )
    
    if movie_id:
        query = query.filter(models.Showtime.movie_id == movie_id)
    
    showtimes = query.offset(skip).limit(limit).all()

    return showtimes

def delete_showtime(showtime_id: int, db: Session):
    db_showtime = db.query(models.Showtime).filter(models.Showtime.id == showtime_id).first()
    
    if not db_showtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")
    
    active_booking_exists = any(
        booking.status == "confirmed" for booking in db_showtime.bookings
    )
    
    if active_booking_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate showtime. There are active bookings for it."
        )

    db_showtime.is_active = False
    db.commit()
    
    return db_showtime