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
    
    # Check for overlapping showtimes
    overlapping_showtime = db.query(models.Showtime).filter(
        or_(
            # New showtime starts during an existing showtime
            and_(
                showtime_data.start_time >= models.Showtime.start_time,
                showtime_data.start_time < models.Showtime.end_time
            ),
            # New showtime ends during an existing showtime
            and_(
                end_time > models.Showtime.start_time,
                end_time <= models.Showtime.end_time
            ),
            # New showtime completely overlaps an existing showtime
            and_(
                showtime_data.start_time <= models.Showtime.start_time,
                end_time >= models.Showtime.end_time
            )
        )
    ).first()
    
    if overlapping_showtime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A showtime already exists from at that timeframe"
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

def get_showtime(db: Session, showtime_id: int, is_admin: bool = False):
    query = db.query(models.Showtime)
    
    if not is_admin:
        query = query.filter(
            models.Showtime.is_active == True
        )
    
    showtime = query.filter(models.Showtime.id == showtime_id).first()
    return showtime

def get_all_showtimes(db: Session, skip: int = 0, limit: int = 100, is_admin: bool = False):
    query = db.query(models.Showtime)
    
    if not is_admin:
        query = query.filter(models.Showtime.is_active == True)
    
    return query.offset(skip).limit(limit).all()

def deactivate_showtime(showtime_id: int, db: Session):
    db_showtime = db.query(models.Showtime).filter(models.Showtime.id == showtime_id).first()
    
    if not db_showtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")
    
    active_booking_exists = any(
        booking.status == "completed" for booking in db_showtime.bookings
    )
    
    if active_booking_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate showtime. There are active bookings for it."
        )

    db_showtime.is_active = False
    db.commit()
    
    return db_showtime

def delete_showtime(showtime_id: int, db: Session):
    db_showtime = db.query(models.Showtime).filter(models.Showtime.id == showtime_id).first()
    
    if not db_showtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")
    
    active_booking_exists = bool(db_showtime.bookings)
    
    if active_booking_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete showtime. There are bookings for it."
        )

    db.delete(db_showtime)
    db.commit()
    
    return db_showtime