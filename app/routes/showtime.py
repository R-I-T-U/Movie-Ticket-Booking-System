from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.database import get_db
from app.auth import get_current_admin_user 
from app.services.showtime_service import get_showtimes, create_showtime, update_showtime, delete_showtime

router = APIRouter(prefix="/showtimes", tags=["showtimes"]) 

@router.get("", response_model=List[schemas.Showtime]) 
async def get_showtimes_endpoint(
    movie_id: Optional[int] = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    showtimes = get_showtimes(db, movie_id=movie_id, skip=skip, limit=limit)
    return showtimes

@router.post("", response_model=schemas.Showtime) 
async def create_showtime_endpoint(
    showtime_data: schemas.ShowtimeCreate,
    current_user: models.User = Depends(get_current_admin_user), 
    db: Session = Depends(get_db)
):
    db_showtime = create_showtime(showtime_data, db)
    return db_showtime 

@router.put("/{showtime_id}", response_model=schemas.Showtime)
async def update_showtime_endpoint(
    showtime_id: int, 
    showtime_data: schemas.ShowtimeCreate,
    current_user: models.User = Depends(get_current_admin_user), 
    db: Session = Depends(get_db)
):
    db_showtime = update_showtime(showtime_id, showtime_data, db)
    return db_showtime  

@router.delete("/{showtime_id}")
async def delete_showtime_endpoint(
    showtime_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    result = delete_showtime(showtime_id, db)
    return {"message": "Showtime deleted successfully"}