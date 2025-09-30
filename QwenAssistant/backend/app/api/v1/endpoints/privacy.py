from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from app.services.privacy_service import privacy_service

router = APIRouter()

class PrivacySettings(BaseModel):
    privacy_level: str = "local_only"  # "local_only", "balanced", "performance"
    data_retention_days: int = 30
    allow_cloud_processing: bool = False

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
    # This is a placeholder implementation
    return PrivacySettings()

@router.post("/settings", response_model=PrivacySettings)
async def update_privacy_settings(settings: PrivacySettings):
    """
    Update privacy settings
    """
    # This is a placeholder implementation
    return settings

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
        "local_processing_threshold": "personal and above are processed locally by default"
    }