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
    
    # Cache (Redis)
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Model paths
    MODEL_PATH: str = "/models"
    
    # Embeddings / Vector index
    EMBEDDING_DIM: int = 768
    EMBEDDING_MODEL_PATH: Optional[str] = None  # If None, defaults to f"{MODEL_PATH}/embedding.onnx" in code
    VECTOR_INDEX_PATH: str = "./data/vector.index"
    VECTOR_META_PATH: str = "./data/vector_meta.json"

    # Budget monitoring
    BUDGET_DAILY_LIMIT_USD: float = 0.0  # 0 means unlimited
    BUDGET_MONTHLY_LIMIT_USD: float = 0.0  # 0 means unlimited
    BUDGET_ENFORCE: bool = False
    COST_PER_TOKEN_USD: float = 0.0  # local inference cost; default 0 for local-only

    # NPU detection override
    NPU_FORCE_ENABLE: bool = False
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
