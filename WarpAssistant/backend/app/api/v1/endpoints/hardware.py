from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.hardware_detector import HardwareDetector

router = APIRouter()

# Initialize hardware detector service
hardware_detector = HardwareDetector()

class HardwareCapability(BaseModel):
    cpu_cores: int
    cpu_architecture: str
    gpu_vendor: Optional[str] = None
    gpu_memory_gb: Optional[float] = None
    total_memory_gb: float
    profile: str  # "light", "medium", "heavy"

class HardwareInfo(BaseModel):
    profile: str
    capabilities: HardwareCapability
    selected_model: str

@router.get("/detect", response_model=HardwareInfo)
async def detect_hardware():
    """
    Detect hardware capabilities and determine appropriate profile
    """
    # Get actual hardware capabilities
    capabilities_dict = hardware_detector.get_capabilities()
    
    # Map the capabilities to our response model
    cpu_info = capabilities_dict["cpu"]
    gpu_info = capabilities_dict["gpu"]
    memory_info = capabilities_dict["memory"]
    
    profile = capabilities_dict["profile"]
    
    # For selected model, we'll use a simple mapping based on profile
    model_mapping = {
        "light": "llama-3.2-3b",
        "medium": "mistral-7b-instruct", 
        "heavy": "llama-3.3-70b",
        "npu-optimized": "optimized-phi-3-mini"
    }
    selected_model = model_mapping.get(profile, "llama-3.2-3b")
    
    hardware_capability = HardwareCapability(
        cpu_cores=cpu_info["cores"],
        cpu_architecture=cpu_info["architecture"],
        gpu_vendor=gpu_info["vendor"] if gpu_info else None,
        gpu_memory_gb=gpu_info["memory_gb"] if gpu_info else None,
        total_memory_gb=memory_info["total_gb"],
        profile=profile
    )
    
    return HardwareInfo(
        profile=profile,
        capabilities=hardware_capability,
        selected_model=selected_model
    )

@router.get("/profile", response_model=str)
async def get_profile():
    """
    Get current hardware profile
    """
    return hardware_detector.get_hardware_profile()