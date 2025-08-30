from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas

def create_movie(movie: schemas.MovieCreate, db: Session):
    # Check if movie with same title already exists (case-insensitive)
    existing_movie = db.query(models.Movie).filter(
        models.Movie.title.ilike(movie.title),
        models.Movie.is_active == True
    ).first()
    
    if existing_movie:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Movie with title '{movie.title}' already exists"
        )
    
    db_movie = models.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def update_movie(movie_id: int, movie: schemas.MovieCreate, db: Session):
    db_movie = db.query(models.Movie).filter(
        models.Movie.id == movie_id,
        models.Movie.is_active == True
    ).first()
    
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # Check if another active movie has the same title (excluding current movie)
    existing_movie = db.query(models.Movie).filter(
        models.Movie.title.ilike(movie.title),
        models.Movie.id != movie_id,
        models.Movie.is_active == True
    ).first()
    
    if existing_movie:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another movie with title '{movie.title}' already exists"
        )
    
    for key, value in movie.model_dump().items():
        setattr(db_movie, key, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

def deactivate_movie(movie_id: int, db: Session):
    db_movie = db.query(models.Movie).filter(
        models.Movie.id == movie_id,
        models.Movie.is_active == True
    ).first()
    
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    for showtime in db_movie.showtimes:
        active_booking_exists = any(
            booking.status == "confirmed" for booking in showtime.bookings
        )
        if active_booking_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot deactivate movie. There are active bookings for showtime ID: {showtime.id}."
            )
    
    db_movie.is_active = False
    db.commit()
    return db_movie

def get_movies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Movie).filter(
        models.Movie.is_active == True
    ).offset(skip).limit(limit).all()

def get_movie(movie_id: int, db: Session):
    return db.query(models.Movie).filter(
        models.Movie.id == movie_id, 
        models.Movie.is_active == True
    ).first()