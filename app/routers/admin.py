from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, crud, auth, models

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
def get_platform_stats(
    current_user = Depends(auth.require_role(models.UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    return crud.get_platform_stats(db)

@router.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(
    current_user = Depends(auth.require_role(models.UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).all()
    return users

@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    current_user = Depends(auth.require_role(models.UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    if user.id == current_user.id:
        raise HTTPException(400, "Cannot deactivate yourself")
    
    user.is_active = False
    db.commit()
    
    return {"message": f"User {user.email} deactivated"}

@router.get("/skills", response_model=List[schemas.SkillResponse])
def get_all_skills(
    current_user = Depends(auth.require_role(models.UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    return crud.get_all_skills(db)