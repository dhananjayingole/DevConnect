from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import schemas, crud, auth, models

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(400, "Email already registered")
    
    db_user = crud.create_user(db, user)
    return db_user

@router.post("/complete-profile/developer", response_model=schemas.DeveloperResponse)
def complete_developer_profile(
    profile: schemas.DeveloperCreate,
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.DEVELOPER:
        raise HTTPException(400, "Profile only for developers")
    
    existing = crud.get_developer_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(400, "Profile already exists. Use PUT to update")
    
    developer = crud.create_developer_profile(db, profile, current_user.id)
    return developer

@router.post("/complete-profile/recruiter", response_model=schemas.RecruiterResponse)
def complete_recruiter_profile(
    profile: schemas.RecruiterCreate,
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.RECRUITER:
        raise HTTPException(400, "Profile only for recruiters")
    
    existing = crud.get_recruiter_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(400, "Profile already exists")
    
    recruiter = crud.create_recruiter_profile(db, profile, current_user.id)
    return recruiter

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, form_data.username)
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(400, "Account is inactive")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 30 * 60,
        "user_role": user.role
    }

@router.post("/refresh")
def refresh_token(
    request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = auth.jwt.decode(
            request.refresh_token,
            auth.settings.REFRESH_SECRET_KEY,
            algorithms=[auth.settings.ALGORITHM]
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(401, "Invalid refresh token")
    except:
        raise HTTPException(401, "Invalid or expired refresh token")
    
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(401, "User not found")
    
    new_access_token = auth.create_access_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60
    }

@router.get("/me")
def get_me(current_user = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active
    }