from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.auth import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/movies", response_model=schemas.Movie)
async def create_movie(
    movie: schemas.MovieCreate,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@router.put("/movies/{movie_id}", response_model=schemas.Movie)
async def update_movie(
    movie_id: int,
    movie: schemas.MovieCreate,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    for key, value in movie.dict().items():
        setattr(db_movie, key, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

@router.delete("/movies/{movie_id}")
async def delete_movie(
    movie_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Soft delete
    movie.is_active = False
    db.commit()
    
    return {"message": "Movie deleted successfully"}

@router.post("/showtimes", response_model=schemas.Showtime)
async def create_showtime(
    showtime: schemas.ShowtimeCreate,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    # Check if movie exists
    movie = db.query(models.Movie).filter(
        models.Movie.id == showtime.movie_id,
        models.Movie.is_active == True
    ).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Calculate end time
    from datetime import timedelta
    end_time = showtime.start_time + timedelta(minutes=movie.duration)
    
    db_showtime = models.Showtime(
        **showtime.dict(),
        end_time=end_time,
        available_seats=showtime.total_seats
    )
    
    db.add(db_showtime)
    db.commit()
    db.refresh(db_showtime)
    return db_showtime

@router.put("/showtimes/{showtime_id}", response_model=schemas.Showtime)
async def update_showtime(
    showtime_id: int,
    showtime: schemas.ShowtimeCreate,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_showtime = db.query(models.Showtime).filter(models.Showtime.id == showtime_id).first()
    
    if not db_showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")
    
    # Check if movie exists
    movie = db.query(models.Movie).filter(
        models.Movie.id == showtime.movie_id,
        models.Movie.is_active == True
    ).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Calculate end time
    from datetime import timedelta
    end_time = showtime.start_time + timedelta(minutes=movie.duration)
    
    # Update available seats if total_seats changed
    if showtime.total_seats != db_showtime.total_seats:
        seats_diff = showtime.total_seats - db_showtime.total_seats
        db_showtime.available_seats += seats_diff
    
    # Update showtime
    for key, value in showtime.dict().items():
        setattr(db_showtime, key, value)
    
    db_showtime.end_time = end_time
    db.commit()
    db.refresh(db_showtime)
    return db_showtime

@router.delete("/showtimes/{showtime_id}")
async def delete_showtime(
    showtime_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    showtime = db.query(models.Showtime).filter(models.Showtime.id == showtime_id).first()
    
    if not showtime:
        raise HTTPException(status_code=404, detail="Showtime not found")
    
    # Soft delete
    showtime.is_active = False
    db.commit()
    
    return {"message": "Showtime deleted successfully"}