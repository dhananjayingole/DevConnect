from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, developers, jobs, admin
from app import models

# Create database tables (only in development)
if settings.DEBUG:
    Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Connect Developers with Recruiters - A complete job platform API",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React frontend
        "http://localhost:8080",      # Android emulator
        "http://127.0.0.1:8000",      # Local development
        settings.FRONTEND_URL,         # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
    max_age=3600,
)

# Include all routers
app.include_router(auth.router)
app.include_router(developers.router)
app.include_router(jobs.router)
app.include_router(admin.router)

# ============ Root Endpoints ============

@app.get("/")
async def root():
    """Welcome endpoint with API information"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": "production" if not settings.DEBUG else "development",
        "endpoints": {
            "authentication": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "refresh": "POST /auth/refresh",
                "my_profile": "GET /auth/me"
            },
            "developers": {
                "my_profile": "GET /developers/profile",
                "update_profile": "PUT /developers/profile",
                "all_developers": "GET /developers/",
                "save_job": "POST /developers/jobs/{job_id}/save",
                "saved_jobs": "GET /developers/me/saved-jobs"
            },
            "jobs": {
                "create": "POST /jobs/",
                "all_jobs": "GET /jobs/",
                "my_jobs": "GET /jobs/my-jobs",
                "job_details": "GET /jobs/{job_id}",
                "close_job": "PUT /jobs/{job_id}/close"
            },
            "admin": {
                "statistics": "GET /admin/stats",
                "all_users": "GET /admin/users",
                "deactivate_user": "PUT /admin/users/{user_id}/deactivate"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "api": "operational"
        }
    }

@app.get("/api/version")
async def api_version():
    """Get API version information"""
    return {
        "version": settings.APP_VERSION,
        "release_date": "2024-01-01",
        "changelog": {
            "1.0.0": "Initial release with authentication, jobs, and developer profiles"
        }
    }

# ============ Startup Event ============

@app.on_event("startup")
async def startup_event():
    """Actions to perform when the application starts"""
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📝 Debug mode: {settings.DEBUG}")
    print(f"🗄️  Database: {settings.DATABASE_URL}")
    print(f"🔗 Frontend URL: {settings.FRONTEND_URL}")
    
    # Create default admin user if not exists (only in development)
    if settings.DEBUG:
        db = SessionLocal()
        try:
            from app import auth as auth_utils
            admin_email = "admin@devconnect.com"
            admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
            
            if not admin_user:
                hashed_password = auth_utils.get_password_hash("Admin@123")
                admin_user = models.User(
                    email=admin_email,
                    hashed_password=hashed_password,
                    role=models.UserRole.ADMIN,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                db.commit()
                print(f"✅ Default admin created: {admin_email} / Admin@123")
        except Exception as e:
            print(f"⚠️ Could not create admin user: {e}")
        finally:
            db.close()


# ============ Shutdown Event ============

@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform when the application shuts down"""
    print(f"🛑 Shutting down {settings.APP_NAME}")

# ============ Error Handlers ============

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": f"Endpoint {request.url.path} not found"
            }
        }
    )