from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db, SessionLocal
from app import models, crud
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

# ============ Common Dependencies ============

async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """Get current user if authenticated, otherwise return None"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if not email:
            return None
    except:
        return None
    
    user = crud.get_user_by_email(db, email)
    return user if user and user.is_active else None


async def get_current_user_required(
    current_user: Optional[models.User] = Depends(get_current_user_optional)
) -> models.User:
    """Require authentication - raises 401 if not authenticated"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_developer(
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
) -> models.Developer:
    """Get current developer profile - requires developer role"""
    if current_user.role != models.UserRole.DEVELOPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires a developer account"
        )
    
    developer = crud.get_developer_by_user_id(db, current_user.id)
    if not developer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer profile not found. Please complete your profile."
        )
    
    return developer


async def get_current_recruiter(
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
) -> models.Recruiter:
    """Get current recruiter profile - requires recruiter role"""
    if current_user.role != models.UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires a recruiter account"
        )
    
    recruiter = crud.get_recruiter_by_user_id(db, current_user.id)
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found. Please complete your profile."
        )
    
    return recruiter


async def get_current_admin(
    current_user: models.User = Depends(get_current_user_required)
) -> models.User:
    """Get current admin - requires admin role"""
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user