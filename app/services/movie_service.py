from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas

def create_movie(movie: schemas.MovieCreate, db: Session):
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

def get_movies(db: Session, skip: int = 0, limit: int = 100, is_admin: bool = False):
    query = db.query(models.Movie)
    if not is_admin:
        query = query.filter(models.Movie.is_active == True)
    
    return query.offset(skip).limit(limit).all()

def get_movie(movie_id: int, db: Session, is_admin: bool = False):
    query = db.query(models.Movie).filter(models.Movie.id == movie_id)
    if not is_admin:
        query = query.filter(models.Movie.is_active == True)
    return query.first()

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
    
    active_showtimes = db.query(models.Showtime).filter(
        models.Showtime.movie_id == movie_id,
        models.Showtime.is_active == True
    ).first()
    
    if active_showtimes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate movie. There are active showtimes associated with this movie."
        )
    
    db_movie.is_active = False
    db.commit()
    return db_movie