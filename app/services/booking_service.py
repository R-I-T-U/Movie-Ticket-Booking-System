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
    
    if showtime.available_seats < booking.seats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Not enough seats available"
        )
    
    db_booking = models.Booking(
        user_id=current_user.id,
        showtime_id=booking.showtime_id,
        seats=booking.seats,
        status="confirmed"  
    )
    
    showtime.available_seats -= booking.seats
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking

def get_user_bookings(current_user: models.User, db: Session):
    bookings = db.query(models.Booking).filter(
        models.Booking.user_id == current_user.id
    ).all()
    
    return bookings

def cancel_booking(booking_id: int, current_user: models.User, db: Session):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Booking not found"
        )
    
    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Booking already cancelled"
        )
    
    booking.status = "cancelled"
    
    showtime = db.query(models.Showtime).filter(
        models.Showtime.id == booking.showtime_id
    ).first()
    
    if showtime:
        showtime.available_seats += booking.seats
    
    db.commit()
    
    return {"message": "Booking cancelled successfully"}