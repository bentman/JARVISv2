from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Local AI Assistant"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "tauri://localhost"
    ]
    
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

    # Retrieval-Augmented Generation (RAG)
    RETRIEVAL_ENABLED: bool = True
    RETRIEVAL_TOP_K: int = 3
    RETRIEVAL_MAX_CHARS: int = 1800

    # Budget monitoring
    BUDGET_DAILY_LIMIT_USD: float = 0.0  # 0 means unlimited
    BUDGET_MONTHLY_LIMIT_USD: float = 0.0  # 0 means unlimited
    BUDGET_ENFORCE: bool = False
    COST_PER_TOKEN_USD: float = 0.0  # local inference cost; default 0 for local-only

    # Privacy
    PRIVACY_SALT: str = os.getenv("PRIVACY_SALT", secrets.token_urlsafe(16))
    PRIVACY_DEFAULT_LEVEL: str = "local_only"  # local_only | balanced | performance
    PRIVACY_REDACT_AGGRESSIVENESS: str = "standard"  # standard | strict
    PRIVACY_RETENTION_DAYS: int = 30
    PRIVACY_ENCRYPT_AT_REST: bool = True

    # Unified search (opt-in)
    SEARCH_ENABLED: bool = False
    SEARCH_PROVIDER: str = "tavily"  # backward-compat
    SEARCH_PROVIDERS: str = "bing,google,tavily"  # priority order CSV
    SEARCH_API_KEY: Optional[str] = None  # Tavily API key
    SEARCH_BING_ENDPOINT: str = "https://api.bing.microsoft.com/v7.0/search"
    SEARCH_BING_API_KEY: Optional[str] = None
    SEARCH_GOOGLE_API_KEY: Optional[str] = None
    SEARCH_GOOGLE_CX: Optional[str] = None
    SEARCH_MAX_RESULTS: int = 5

    # Remote LLM synthesis (opt-in)
    REMOTE_LLM_ENABLED: bool = False
    REMOTE_LLM_PROVIDER: Optional[str] = None  # openai|anthropic|gemini|xai
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = None
    XAI_API_KEY: Optional[str] = None
    XAI_MODEL: Optional[str] = None
    BUDGET_LLM_WEB_COST_PER_TOKEN_USD: float = 0.0

    # NPU detection override
    NPU_FORCE_ENABLE: bool = False
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
