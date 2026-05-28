import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    #Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./devconnect.db")

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production-12345")
    REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY","your-refresh-secret-key-change-this-67890")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    # App
    APP_NAME = "DevConnect API"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG","TRUE") == "True"

    # frontend URL
    FRONTEND_URL = os.getenv("FRONTEND_URL","http://localhost:3000")

settings = Settings()