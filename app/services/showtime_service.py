from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas

def create_showtime(showtime_data: schemas.ShowtimeCreate, db: Session):
    movie = db.query(models.Movie).filter(
        models.Movie.id == showtime_data.movie_id,
        models.Movie.is_active == True
    ).first()
    
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    end_time = showtime_data.start_time + timedelta(minutes=movie.duration)
    
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