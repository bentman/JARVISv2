import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any
import os

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    """Setup logging configuration based on environment"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "text").lower()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        # Standard format for development
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # File handlers for production
    if os.getenv("ENV") == "production":
        # Error log
        error_handler = logging.FileHandler("/app/data/logs/error.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)
        
        # General log
        info_handler = logging.FileHandler("/app/data/logs/app.log")
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(info_handler)
    
    # Silence noisy libraries in production
    if os.getenv("ENV") == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("faiss").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        
    return root_logger

# Logging utilities for request tracking
class RequestLogger:
    """Helper class for request-specific logging"""
    
    def __init__(self, logger: logging.Logger, request_id: str = None, endpoint: str = None):
        self.logger = logger
        self.request_id = request_id
        self.endpoint = endpoint
    
    def info(self, message: str, **kwargs):
        extra = {"request_id": self.request_id, "endpoint": self.endpoint}
        extra.update(kwargs)
        self.logger.info(message, extra=extra)
        
    def error(self, message: str, exc_info=None, **kwargs):
        extra = {"request_id": self.request_id, "endpoint": self.endpoint}
        extra.update(kwargs)
        self.logger.error(message, exc_info=exc_info, extra=extra)
        
    def warning(self, message: str, **kwargs):
        extra = {"request_id": self.request_id, "endpoint": self.endpoint}
        extra.update(kwargs)
        self.logger.warning(message, extra=extra)