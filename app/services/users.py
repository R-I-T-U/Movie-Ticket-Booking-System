from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import models, schemas
from app.auth import get_password_hash, verify_password, create_access_token
from app.config import settings

def create_user(user: schemas.UserCreate, db: Session):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        return None  

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        return None 
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return access_token