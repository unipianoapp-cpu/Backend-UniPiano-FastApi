from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Piano Learning API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".m4a", ".ogg"]
    UPLOAD_DIR: str = "uploads"
    
    # Audio processing settings
    SAMPLE_RATE: int = 44100
    AUDIO_CHUNK_SIZE: int = 1024
    
    # AI/ML settings
    MODEL_PATH: str = "models"
    PITCH_DETECTION_MODEL: str = "crepe"
    
    # Redis settings (for caching and task queue)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
