from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    FRONTEND_URL: str = Field(default=os.getenv("FRONTEND_URL", "http://localhost:5173"))
    BACKEND_URL: str = Field(default=os.getenv("BACKEND_URL", "http://localhost:8000"))

    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default=os.getenv("GOOGLE_CLIENT_ID", ""))
    GOOGLE_CLIENT_SECRET: str = Field(default=os.getenv("GOOGLE_CLIENT_SECRET", ""))
    GOOGLE_REDIRECT_URI: str = Field(default=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"))

    # DB
    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///db/app.db"))

    # Security
    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY", "dev-secret-key"))

    # HF models
    INTENT_MODEL: str = Field(default=os.getenv("INTENT_MODEL", "facebook/bart-large-mnli"))
    NER_MODEL: str = Field(default=os.getenv("NER_MODEL", "google/flan-t5-base"))

settings = Settings()
