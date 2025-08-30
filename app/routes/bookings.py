from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.auth import get_current_active_user  
from app.services.booking_service import create_booking, get_user_bookings, cancel_booking

router = APIRouter(prefix="/bookings", tags=["bookings"])  # Changed prefix

@router.post("", response_model=schemas.Booking)
async def create_booking_endpoint(
    booking: schemas.BookingCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return create_booking(booking, current_user, db)

@router.get("", response_model=List[schemas.BookingWithDetails])
async def get_user_bookings_endpoint(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return get_user_bookings(current_user, db)

@router.delete("/{booking_id}")
async def cancel_booking_endpoint(
    booking_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return cancel_booking(booking_id, current_user, db)