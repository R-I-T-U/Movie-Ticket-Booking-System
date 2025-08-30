from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.auth import get_current_admin_user  
from app.services.movie_service import get_movies, get_movie, create_movie, update_movie, deactivate_movie

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=List[schemas.Movie])  
async def get_movies_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_movies(db, skip=skip, limit=limit)

@router.get("/{movie_id}", response_model=schemas.Movie)
async def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    if movie_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid movie ID")
    
    db_movie = get_movie(movie_id, db)
    
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return db_movie

@router.post("", response_model=schemas.Movie, status_code=status.HTTP_201_CREATED)  
async def create_movie_endpoint(
    movie: schemas.MovieCreate, 
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        return create_movie(movie, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create movie"
        )

@router.put("/{movie_id}", response_model=schemas.Movie)
async def update_movie_endpoint(
    movie_id: int, 
    movie: schemas.MovieCreate, 
    current_user: models.User = Depends(get_current_admin_user), 
    db: Session = Depends(get_db)
):
    if movie_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid movie ID")
    try:
        return update_movie(movie_id, movie, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update movie"
        )

@router.delete("/{movie_id}", status_code=status.HTTP_200_OK)
async def delete_movie_endpoint(
    movie_id: int, 
    current_user: models.User = Depends(get_current_admin_user), 
    db: Session = Depends(get_db)
):
    if movie_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid movie ID")
    try:
        result = deactivate_movie(movie_id, db)
        return {"message": "Movie deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete movie"
        )