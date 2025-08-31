from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from datetime import datetime, timedelta
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
        raise HTTPException(status_code=404, detail="Showtime not found")
    
    movie = db.query(models.Movie).filter(
        models.Movie.id == showtime_data.movie_id,
        models.Movie.is_active == True
    ).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    end_time = showtime_data.start_time + timedelta(minutes=movie.duration)
    
    # Store original values for comparison
    original_total_seats = db_showtime.total_seats
    original_available_seats = db_showtime.available_seats
    
    # Update all fields except seats
    for key, value in showtime_data.model_dump().items():
        if key not in ['total_seats', 'available_seats']:
            setattr(db_showtime, key, value)
    
    # Handle total seats change
    if showtime_data.total_seats != original_total_seats:
        # Calculate how many seats are currently booked
        booked_seats = original_total_seats - original_available_seats
        
        # Update total seats
        db_showtime.total_seats = showtime_data.total_seats
        
        # Recalculate available seats (total - booked)
        db_showtime.available_seats = showtime_data.total_seats - booked_seats
        
        # Ensure available seats doesn't go negative
        if db_showtime.available_seats < 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot reduce total seats below currently booked seats"
            )
    
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
    
    # Check if showtime has completed (end time has passed)
    current_time = datetime.now(db_showtime.end_time.tzinfo)
    has_completed = current_time > db_showtime.end_time
    
    # Check for active bookings (only "completed" status bookings matter for active showtimes)
    active_booking_exists = any(
        booking.status == "completed" for booking in db_showtime.bookings
    )
    
    # Allow deactivation if showtime has completed OR there are no active bookings
    if not has_completed and active_booking_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate showtime. There are active bookings and showtime hasn't completed yet."
        )

    db_showtime.is_active = False
    db.commit()
    
    return db_showtime

def delete_showtime(showtime_id: int, db: Session):
    db_showtime = db.query(models.Showtime).filter(models.Showtime.id == showtime_id).first()
    
    if not db_showtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")
    
    # Check if showtime has completed (end time has passed)
    current_time = datetime.now(db_showtime.end_time.tzinfo)
    has_completed = current_time > db_showtime.end_time
    
    # Check if showtime is inactive
    is_inactive = not db_showtime.is_active
    
    # Check for any bookings
    has_any_bookings = bool(db_showtime.bookings)
    
    # Allow deletion if:
    # 1. Showtime is inactive OR has completed, AND
    # 2. There are no bookings at all
    if (is_inactive or has_completed) and not has_any_bookings:
        # Safe to delete
        db.delete(db_showtime)
        db.commit()
        return db_showtime
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete showtime. It must be either inactive or completed, and have no bookings."
        )