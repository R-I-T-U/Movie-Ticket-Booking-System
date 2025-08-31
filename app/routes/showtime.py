from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.auth import get_current_admin_user, get_current_user 
from app.services.showtime_service import deactivate_showtime, get_all_showtimes, create_showtime, get_showtime, update_showtime, delete_showtime

router = APIRouter(prefix="/showtimes", tags=["showtimes"]) 

@router.get("", response_model=List[schemas.Showtime])
async def get_all_showtimes_endpoint(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    showtimes = get_all_showtimes(db, skip=skip, limit=limit, is_admin=current_user.is_admin)
    return showtimes

@router.get("/{showtime_id}", response_model=schemas.Showtime)
async def get_showtime_by_id_endpoint(
    showtime_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    showtime = get_showtime(
        db, 
        showtime_id=showtime_id, 
        is_admin=current_user.is_admin)
    
    if not showtime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Showtime not found"
        )
    
    return showtime

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
    if showtime_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid showtime ID")
    db_showtime = update_showtime(showtime_id, showtime_data, db)
    return db_showtime  

@router.delete("/{showtime_id}")
async def delete_showtime_endpoint(
    showtime_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if showtime_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid showtime ID")
    result = delete_showtime(showtime_id, db)
    return {"message": "Showtime deleted successfully"}

@router.patch("/{showtime_id}/deactivate")
async def deactivate_showtime_endpoint(
    showtime_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    if showtime_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid showtime ID")
    result = deactivate_showtime(showtime_id, db)
    return {"message": "Showtime deactivated successfully"}