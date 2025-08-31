from datetime import datetime
from fastapi import HTTPException, status
from app import models, schemas
from sqlalchemy.orm import Session

def create_booking(booking: schemas.BookingCreate, current_user: models.User, db: Session):
    showtime = db.query(models.Showtime).filter(
        models.Showtime.id == booking.showtime_id,
        models.Showtime.is_active == True
    ).first()
    
    if not showtime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Showtime not found")
    
    current_time = datetime.now(showtime.end_time.tzinfo)
    if current_time > showtime.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot book. The showtime has already ended."
        )

    if showtime.available_seats < booking.seats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Not enough seats available"
        )
    
    db_booking = models.Booking(
        user_id=current_user.id,
        showtime_id=booking.showtime_id,
        seats=booking.seats,
        status="completed"  
    )
    
    showtime.available_seats -= booking.seats
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking

def get_user_bookings(db: Session, current_user: models.User, is_admin: bool = False):
    if is_admin:
        bookings = db.query(models.Booking).all()
    else:
        bookings = db.query(models.Booking).filter(
            models.Booking.user_id == current_user.id
        ).all()
    
    return bookings

from datetime import datetime, timedelta

def cancel_booking(booking_id: int, current_user: models.User, db: Session):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="You can cancel only your own bookings"
        )
    
    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Booking already cancelled"
        )
    
    # Get the related showtime
    showtime = db.query(models.Showtime).filter(
        models.Showtime.id == booking.showtime_id
    ).first()
    
    if not showtime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Showtime not found"
        )
    
    # Check if showtime is about to start within 30 minutes
    current_time = datetime.now(showtime.start_time.tzinfo)  # Handle timezone awareness
    time_until_showtime = showtime.start_time - current_time
    
    if time_until_showtime <= timedelta(minutes=30):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot cancel booking. The showtime starts in less than 30 minutes."
        )
    
    # Proceed with cancellation
    booking.status = "cancelled"
    
    # Return seats to available seats
    showtime.available_seats += booking.seats
    
    db.commit()
    
    return {"message": "Booking cancelled successfully"}

def delete_booking(booking_id: int, current_user: models.User, db: Session):
    # Get the booking
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="You can only delete your own bookings"
        )
    
    showtime = db.query(models.Showtime).filter(
        models.Showtime.id == booking.showtime_id
    ).first()
    
    if not showtime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Showtime not found"
        )
    
    if booking.status == "completed":
        current_time = datetime.now(showtime.end_time.tzinfo)
        if showtime.end_time > current_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot delete booking. The showtime has not yet completed."
            )
    
    db.delete(booking)
    db.commit()
    
    return {"message": "Booking deleted successfully"}