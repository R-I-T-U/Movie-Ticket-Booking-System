from sqlalchemy.orm import Session
from app import models
from app.auth import get_password_hash
from app.database import SessionLocal


def create_admin():
    db: Session = SessionLocal()
    admin_user = models.User(
        username="admin",
        email="admin@gmail.com",
        full_name="admin",
        hashed_password=get_password_hash("admin"),
        is_active=True,
        is_admin=True 
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print(f"Admin user created: {admin_user.username}")

if __name__ == "__main__":
    create_admin()