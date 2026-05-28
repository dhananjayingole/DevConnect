from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import json

from app import models, schemas, auth

# ============ User CRUD ============
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ============ Developer CRUD ============
def create_developer_profile(db: Session, developer_data: schemas.DeveloperCreate, user_id: int):
    developer = models.Developer(
        user_id=user_id,
        full_name=developer_data.full_name,
        title=developer_data.title,
        bio=developer_data.bio,
        location=developer_data.location,
        experience_years=developer_data.experience_years or 0,
        experience_level=developer_data.experience_level,
        github_url=developer_data.github_url,
        linkedin_url=developer_data.linkedin_url,
        portfolio_url=developer_data.portfolio_url
    )
    db.add(developer)
    db.flush()
    
    if developer_data.skills:
        for skill_name in developer_data.skills:
            skill = get_or_create_skill(db, skill_name)
            if skill not in developer.skills:
                developer.skills.append(skill)
    
    db.commit()
    db.refresh(developer)
    return developer

def get_developer_by_user_id(db: Session, user_id: int):
    return db.query(models.Developer).filter(models.Developer.user_id == user_id).first()

def get_developer_by_id(db: Session, developer_id: int):
    return db.query(models.Developer).filter(models.Developer.id == developer_id).first()

def update_developer_profile(db: Session, developer_id: int, update_data: schemas.DeveloperUpdate):
    developer = get_developer_by_id(db, developer_id)
    if not developer:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(developer, key, value)
    
    db.commit()
    db.refresh(developer)
    return developer

def get_all_developers(db: Session, skip: int = 0, limit: int = 100, skill: str = None):
    query = db.query(models.Developer)
    if skill:
        query = query.join(models.Developer.skills).filter(models.Skill.name == skill)
    return query.offset(skip).limit(limit).all()

# ============ Skill CRUD ============
def get_or_create_skill(db: Session, skill_name: str):
    skill = db.query(models.Skill).filter(models.Skill.name == skill_name).first()
    if not skill:
        skill = models.Skill(name=skill_name)
        db.add(skill)
        db.commit()
        db.refresh(skill)
    return skill

def get_all_skills(db: Session):
    return db.query(models.Skill).order_by(models.Skill.name).all()

# ============ Recruiter CRUD ============
def create_recruiter_profile(db: Session, recruiter_data: schemas.RecruiterCreate, user_id: int):
    recruiter = models.Recruiter(
        user_id=user_id,
        company_name=recruiter_data.company_name,
        company_website=recruiter_data.company_website,
        company_size=recruiter_data.company_size,
        industry=recruiter_data.industry,
        position=recruiter_data.position,
        phone=recruiter_data.phone
    )
    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)
    return recruiter

def get_recruiter_by_user_id(db: Session, user_id: int):
    return db.query(models.Recruiter).filter(models.Recruiter.user_id == user_id).first()

def get_recruiter_by_id(db: Session, recruiter_id: int):
    return db.query(models.Recruiter).filter(models.Recruiter.id == recruiter_id).first()

# ============ Job CRUD ============
def create_job(db: Session, job_data: schemas.JobCreate, recruiter_id: int):
    db_job = models.Job(
        recruiter_id=recruiter_id,
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        location=job_data.location,
        job_type=job_data.job_type,
        experience_level=job_data.experience_level,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        skills_required=job_data.skills_required,
        expires_at=job_data.expires_at
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs(db: Session, skip: int = 0, limit: int = 100, job_type: str = None, location: str = None):
    query = db.query(models.Job).filter(models.Job.is_active == True)
    if job_type:
        query = query.filter(models.Job.job_type == job_type)
    if location:
        query = query.filter(models.Job.location.contains(location))
    return query.order_by(models.Job.created_at.desc()).offset(skip).limit(limit).all()

def get_job_by_id(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def get_jobs_by_recruiter(db: Session, recruiter_id: int):
    return db.query(models.Job).filter(models.Job.recruiter_id == recruiter_id).all()

def update_job_status(db: Session, job_id: int, is_active: bool):
    job = get_job_by_id(db, job_id)
    if job:
        job.is_active = is_active
        db.commit()
        db.refresh(job)
    return job

def increment_job_views(db: Session, job_id: int):
    job = get_job_by_id(db, job_id)
    if job:
        job.views += 1
        db.commit()

# ============ Saved Jobs CRUD ============
def save_job(db: Session, developer_id: int, job_id: int):
    developer = get_developer_by_id(db, developer_id)
    job = get_job_by_id(db, job_id)
    
    if not developer or not job:
        return False
    
    if job not in developer.saved_jobs:
        developer.saved_jobs.append(job)
        db.commit()
        return True
    return False

def unsave_job(db: Session, developer_id: int, job_id: int):
    developer = get_developer_by_id(db, developer_id)
    job = get_job_by_id(db, job_id)
    
    if developer and job and job in developer.saved_jobs:
        developer.saved_jobs.remove(job)
        db.commit()
        return True
    return False

def get_saved_jobs(db: Session, developer_id: int):
    developer = get_developer_by_id(db, developer_id)
    return developer.saved_jobs if developer else []

# ============ Admin Analytics ============
def get_platform_stats(db: Session):
    total_users = db.query(models.User).count()
    total_developers = db.query(models.Developer).count()
    total_recruiters = db.query(models.Recruiter).count()
    total_jobs = db.query(models.Job).count()
    active_jobs = db.query(models.Job).filter(models.Job.is_active == True).count()
    
    return {
        "total_users": total_users,
        "total_developers": total_developers,
        "total_recruiters": total_recruiters,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs
    }