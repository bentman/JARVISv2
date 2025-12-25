from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from app.services.privacy_service import privacy_service

router = APIRouter()

class PrivacySettings(BaseModel):
    privacy_level: str = "local_only"  # "local_only", "balanced", "performance"
    data_retention_days: int = 30
    redact_aggressiveness: str = "standard"  # "standard", "strict"

class DataClassificationRequest(BaseModel):
    content: str

class DataClassificationResponse(BaseModel):
    content: str
    classification: str  # "sensitive", "personal", "public", "restricted"
    should_process_locally: bool
    redacted_content: str

class ProcessingEnforcementResponse(BaseModel):
    classification: str
    should_process_locally: bool
    redacted_content: str
    original_content_preserved: bool

@router.get("/settings", response_model=PrivacySettings)
async def get_privacy_settings():
    """
    Get current privacy settings
    """
    cfg = privacy_service.get_settings()
    return PrivacySettings(
        privacy_level=cfg["privacy_level"],
        data_retention_days=cfg["data_retention_days"],
        redact_aggressiveness=cfg["redact_aggressiveness"],
    )

@router.post("/settings", response_model=PrivacySettings)
async def update_privacy_settings(settings: PrivacySettings):
    """
    Update privacy settings
    """
    cfg = privacy_service.set_settings(
        privacy_level=settings.privacy_level,
        data_retention_days=settings.data_retention_days,
        redact_aggressiveness=settings.redact_aggressiveness,
    )
    return PrivacySettings(
        privacy_level=cfg["privacy_level"],
        data_retention_days=cfg["data_retention_days"],
        redact_aggressiveness=cfg["redact_aggressiveness"],
    )

@router.post("/classify", response_model=DataClassificationResponse)
async def classify_data(request: DataClassificationRequest):
    """
    Classify data based on sensitivity and provide processing recommendations
    """
    classification = privacy_service.classify_data(request.content)
    should_process_locally = privacy_service.should_process_locally(request.content)
    redacted_content = privacy_service.redact_sensitive_data(request.content)
    
    return DataClassificationResponse(
        content=request.content,
        classification=classification.value,
        should_process_locally=should_process_locally,
        redacted_content=redacted_content
    )

@router.post("/enforce-local-processing", response_model=ProcessingEnforcementResponse)
async def enforce_local_processing(request: DataClassificationRequest):
    """
    Enforce local processing based on data sensitivity
    """
    result = privacy_service.enforce_local_processing(request.content)
    
    return ProcessingEnforcementResponse(
        classification=result["classification"],
        should_process_locally=result["should_process_locally"],
        redacted_content=result["redacted_content"],
        original_content_preserved=result["original_content_preserved"]
    )

@router.post("/redact-sensitive-data", response_model=DataClassificationResponse)
async def redact_sensitive_data(request: DataClassificationRequest):
    """
    Redact sensitive information from content
    """
    classification = privacy_service.classify_data(request.content)
    redacted_content = privacy_service.redact_sensitive_data(request.content)
    
    return DataClassificationResponse(
        content=request.content,
        classification=classification.value,
        should_process_locally=True,  # Data has been redacted for local processing
        redacted_content=redacted_content
    )

@router.get("/classification-info")
async def get_classification_info():
    """
    Get information about data classification system
    """
    return {
        "classifications": ["public", "personal", "sensitive", "restricted"],
        "description": "Data is classified based on sensitivity to determine processing requirements",
        "local_processing_threshold": "personal and above are processed locally by default",
        "privacy_levels": ["local_only", "balanced", "performance"],
        "redact_aggressiveness": ["standard", "strict"]
    }

@router.post("/cleanup")
async def cleanup_retention():
    """
    Delete messages older than the configured data_retention_days.
    """
    cfg = privacy_service.get_settings()
    days = cfg["data_retention_days"]
    deleted = privacy_service.delete_messages_older_than(days)
    return {"deleted": deleted, "days": days}
