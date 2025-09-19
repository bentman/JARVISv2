from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Local AI Assistant"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/local_ai.db"
    
    # Model paths
    MODEL_PATH: str = "/models"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()