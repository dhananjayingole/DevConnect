from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas, crud, auth, models

router = APIRouter(prefix="/developers", tags=["Developers"])

@router.get("/profile", response_model=schemas.DeveloperResponse)
def get_my_profile(
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.DEVELOPER:
        raise HTTPException(400, "Not a developer account")
    
    developer = crud.get_developer_by_user_id(db, current_user.id)
    if not developer:
        raise HTTPException(404, "Profile not found. Please complete your profile")
    
    return developer

@router.put("/profile", response_model=schemas.DeveloperResponse)
def update_my_profile(
    profile: schemas.DeveloperUpdate,
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.DEVELOPER:
        raise HTTPException(400, "Not a developer account")
    
    developer = crud.get_developer_by_user_id(db, current_user.id)
    if not developer:
        raise HTTPException(404, "Profile not found")
    
    updated = crud.update_developer_profile(db, developer.id, profile)
    return updated

@router.get("/", response_model=List[schemas.DeveloperResponse])
def get_all_developers(
    skip: int = 0,
    limit: int = 100,
    skill: Optional[str] = Query(None, description="Filter by skill"),
    db: Session = Depends(get_db)
):
    developers = crud.get_all_developers(db, skip, limit, skill)
    return developers

@router.get("/{developer_id}", response_model=schemas.DeveloperResponse)
def get_developer_by_id(
    developer_id: int,
    db: Session = Depends(get_db)
):
    developer = crud.get_developer_by_id(db, developer_id)
    if not developer:
        raise HTTPException(404, "Developer not found")
    return developer

@router.post("/jobs/{job_id}/save", response_model=schemas.SaveJobResponse)
def save_job(
    job_id: int,
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.DEVELOPER:
        raise HTTPException(400, "Only developers can save jobs")
    
    developer = crud.get_developer_by_user_id(db, current_user.id)
    if not developer:
        raise HTTPException(404, "Developer profile not found")
    
    saved = crud.save_job(db, developer.id, job_id)
    if not saved:
        raise HTTPException(400, "Job not found or already saved")
    
    return {"message": "Job saved successfully", "saved": True}

@router.delete("/jobs/{job_id}/unsave", response_model=schemas.SaveJobResponse)
def unsave_job(
    job_id: int,
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.DEVELOPER:
        raise HTTPException(400, "Only developers can unsave jobs")
    
    developer = crud.get_developer_by_user_id(db, current_user.id)
    if not developer:
        raise HTTPException(404, "Developer profile not found")
    
    unsaved = crud.unsave_job(db, developer.id, job_id)
    if not unsaved:
        raise HTTPException(400, "Job not found or not saved")
    
    return {"message": "Job removed from saved", "saved": False}

@router.get("/me/saved-jobs", response_model=List[schemas.JobResponse])
def get_my_saved_jobs(
    current_user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != models.UserRole.DEVELOPER:
        raise HTTPException(400, "Only developers have saved jobs")
    
    developer = crud.get_developer_by_user_id(db, current_user.id)
    if not developer:
        raise HTTPException(404, "Developer profile not found")
    
    jobs = crud.get_saved_jobs(db, developer.id)
    
    # Add company name to each job
    result = []
    for job in jobs:
        recruiter = crud.get_recruiter_by_id(db, job.recruiter_id)
        job_dict = {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "location": job.location,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "skills_required": job.skills_required,
            "is_active": job.is_active,
            "views": job.views,
            "created_at": job.created_at,
            "expires_at": job.expires_at,
            "recruiter_id": job.recruiter_id,
            "company_name": recruiter.company_name if recruiter else None
        }
        result.append(schemas.JobResponse(**job_dict))
    
    return result