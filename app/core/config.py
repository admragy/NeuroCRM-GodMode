"""
Application Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "OmniCRM God Mode"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database (optional)
    DATABASE_URL: Optional[str] = None
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    
    # AI Providers (optional)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
