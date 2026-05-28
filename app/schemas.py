from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    DEVELOPER = "developer"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"

class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    REMOTE = "remote"

# user schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Skill Schemas
class SkillResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

# Developer Schemas
class DeveloperCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    title: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = 0
    experience_level: Optional[ExperienceLevel] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = None

class DeveloperUpdate(BaseModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    experience_level: Optional[ExperienceLevel] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    is_available: Optional[bool] = None

class DeveloperResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    title: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    experience_years: int
    experience_level: Optional[ExperienceLevel]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    is_available: bool
    skills: List[SkillResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# ============ Recruiter Schemas ============
class RecruiterCreate(BaseModel):
    company_name: str = Field(..., min_length=2)
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    position: str
    phone: Optional[str] = None

class RecruiterResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    company_website: Optional[str]
    company_size: Optional[str]
    industry: Optional[str]
    position: str
    phone: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

# ============ Job Schemas ============
class JobBase(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=20)
    requirements: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    skills_required: Optional[str] = None
    expires_at: Optional[datetime] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    recruiter_id: int
    is_active: bool
    views: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    company_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ============ Save Job Schemas ============
class SaveJobResponse(BaseModel):
    message: str
    saved: bool

# ============ Auth Schemas ============
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_role: UserRole

class RefreshTokenRequest(BaseModel):
    refresh_token: str