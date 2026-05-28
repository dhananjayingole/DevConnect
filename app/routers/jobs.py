from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas, crud, auth, models

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=schemas.JobResponse, status_code=201)
def create_job(
    job: schemas.JobCreate,
    current_user = Depends(auth.require_role(models.UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    recruiter = crud.get_recruiter_by_user_id(db, current_user.id)
    if not recruiter:
        raise HTTPException(404, "Recruiter profile not found. Please complete your profile")
    
    db_job = crud.create_job(db, job, recruiter.id)
    
    # Add company name to response
    response_dict = {
        "id": db_job.id,
        "title": db_job.title,
        "description": db_job.description,
        "requirements": db_job.requirements,
        "location": db_job.location,
        "job_type": db_job.job_type,
        "experience_level": db_job.experience_level,
        "salary_min": db_job.salary_min,
        "salary_max": db_job.salary_max,
        "skills_required": db_job.skills_required,
        "is_active": db_job.is_active,
        "views": db_job.views,
        "created_at": db_job.created_at,
        "expires_at": db_job.expires_at,
        "recruiter_id": db_job.recruiter_id,
        "company_name": recruiter.company_name
    }
    
    return schemas.JobResponse(**response_dict)

@router.get("/", response_model=List[schemas.JobResponse])
def get_all_jobs(
    skip: int = 0,
    limit: int = 100,
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    location: Optional[str] = Query(None, description="Filter by location"),
    db: Session = Depends(get_db)
):
    jobs = crud.get_jobs(db, skip, limit, job_type, location)
    
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

@router.get("/my-jobs", response_model=List[schemas.JobResponse])
def get_my_jobs(
    current_user = Depends(auth.require_role(models.UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    recruiter = crud.get_recruiter_by_user_id(db, current_user.id)
    if not recruiter:
        raise HTTPException(404, "Recruiter profile not found")
    
    jobs = crud.get_jobs_by_recruiter(db, recruiter.id)
    
    result = []
    for job in jobs:
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
            "company_name": recruiter.company_name
        }
        result.append(schemas.JobResponse(**job_dict))
    
    return result

@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job_by_id(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    
    crud.increment_job_views(db, job_id)
    
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
    
    return schemas.JobResponse(**job_dict)

@router.put("/{job_id}/close")
def close_job(
    job_id: int,
    current_user = Depends(auth.require_role(models.UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    job = crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    
    recruiter = crud.get_recruiter_by_user_id(db, current_user.id)
    if not recruiter:
        raise HTTPException(404, "Recruiter profile not found")
    
    if job.recruiter_id != recruiter.id:
        raise HTTPException(403, "You can only close your own jobs")
    
    crud.update_job_status(db, job_id, False)
    return {"message": "Job closed successfully"}