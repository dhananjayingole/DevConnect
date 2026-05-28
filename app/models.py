from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    DEVELOPER = "developer"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class ExperienceLevel(str, enum.Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"

class JobType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    REMOTE = "remote"

# ============ Association Tables ============
developer_skills = Table(
    'developer_skills',
    Base.metadata,
    Column('developer_id', Integer, ForeignKey('developers.id', ondelete='CASCADE')),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'))
)

saved_jobs = Table(
    'saved_jobs',
    Base.metadata,
    Column('developer_id', Integer, ForeignKey('developers.id', ondelete='CASCADE')),
    Column('job_id', Integer, ForeignKey('jobs.id', ondelete='CASCADE')),
    Column('saved_at', DateTime, server_default=func.now())
)

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_login = Column(DateTime)

    # Relationships
    developer = relationship("Developer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recruiter = relationship("Recruiter", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Developer(Base):
    __tablename__ = "developers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String(200), nullable=False)
    title = Column(String(200))
    bio = Column(Text)
    location = Column(String(200))
    experience_years = Column(Integer, default=0)
    experience_level = Column(Enum(ExperienceLevel))
    github_url = Column(String(500))
    linkedin_url = Column(String(500))
    portfolio_url = Column(String(500))
    profile_pic = Column(String(500))
    is_available = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="developer")
    skills = relationship("Skill", secondary=developer_skills, back_populates="developers")
    saved_jobs = relationship("Job", secondary=saved_jobs, back_populates="saved_by")

class Recruiter(Base):
    __tablename__ = "recruiters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String(200), nullable=False)
    company_website = Column(String(500))
    company_size = Column(String(50))
    industry = Column(String(100))
    position = Column(String(200))
    phone = Column(String(20))
    
    # relationship
    user = relationship("User", back_populates="recruiter")
    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    developers = relationship("Developer", secondary=developer_skills, back_populates="skills")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id", ondelete="CASCADE"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    location = Column(String(200))
    job_type = Column(Enum(JobType), nullable=False)
    experience_level = Column(Enum(ExperienceLevel))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    skills_required = Column(Text)
    is_active = Column(Boolean, default=True)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)

    recruiter = relationship("Recruiter", back_populates="jobs")
    saved_by = relationship("Developer", secondary=saved_jobs, back_populates="saved_jobs")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)