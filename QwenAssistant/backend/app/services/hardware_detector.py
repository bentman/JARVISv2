import psutil
import GPUtil
import platform
from typing import Dict, Optional, List

class HardwareDetector:
    """
    Detects hardware capabilities and determines appropriate profile
    """
    
    def __init__(self):
        self.cpu_info = self._get_cpu_info()
        self.gpu_info = self._get_gpu_info()
        self.memory_info = self._get_memory_info()
        self.accel_providers = self._get_runtime_providers()
        
    def _get_cpu_info(self) -> Dict:
        """Get CPU information"""
        return {
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "architecture": platform.machine(),
            "frequency": psutil.cpu_freq().max if psutil.cpu_freq() else 0
        }
        
    def _get_gpu_info(self) -> Optional[Dict]:
        """Get GPU information"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU for now
                return {
                    "name": gpu.name,
                    "memory_gb": round(gpu.memoryTotal / 1024, 2),
                    "vendor": self._detect_gpu_vendor(gpu.name)
                }
        except Exception:
            pass
        # Fallback: try vendor from onnxruntime providers
        try:
            providers = self._get_runtime_providers()
            if any('CUDAExecutionProvider' in p for p in providers):
                return {"name": "NVIDIA (provider)", "memory_gb": 0, "vendor": "nvidia"}
            if any('ROCMExecutionProvider' in p for p in providers):
                return {"name": "AMD ROCm (provider)", "memory_gb": 0, "vendor": "amd"}
            if any('DmlExecutionProvider' in p for p in providers):
                return {"name": "DirectML (provider)", "memory_gb": 0, "vendor": "microsoft"}
            if any('CoreMLExecutionProvider' in p for p in providers):
                return {"name": "Apple CoreML (provider)", "memory_gb": 0, "vendor": "apple"}
        except Exception:
            pass
        return None
        
    def _detect_gpu_vendor(self, gpu_name: str) -> str:
        """Detect GPU vendor from name"""
        gpu_name_lower = gpu_name.lower()
        if "nvidia" in gpu_name_lower:
            return "nvidia"
        elif "amd" in gpu_name_lower or "radeon" in gpu_name_lower:
            return "amd"
        elif "intel" in gpu_name_lower:
            return "intel"
        else:
            return "unknown"
            
    def _get_memory_info(self) -> Dict:
        """Get memory information"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2)
        }
        
    def get_hardware_profile(self) -> str:
        """
        Determine hardware profile based on capabilities
        Returns: "light", "medium", "heavy", or "npu-optimized"
        """
        # Check for NPU first (specialized processors)
        if self._has_npu():
            return "npu-optimized"
        
        # Prefer known accelerators from runtime providers
        providers = self.accel_providers or []
        if any(p for p in providers if any(x in p for x in ("CUDAExecutionProvider","ROCMExecutionProvider","DmlExecutionProvider","CoreMLExecutionProvider"))):
            # If accelerator present, scale by system memory
            if self.memory_info["total_gb"] >= 16:
                return "heavy"
            return "medium"
        
        # Check for GPU with memory heuristic
        if self.gpu_info and self.gpu_info.get("memory_gb", 0) >= 8:
            if self.memory_info["total_gb"] >= 16:
                return "heavy"
            else:
                return "medium"
        elif self.gpu_info and self.gpu_info.get("memory_gb", 0) >= 4:
            return "medium"
        else:
            # Check CPU and memory for light/medium classification
            if self.cpu_info["cores"] >= 8 and self.memory_info["total_gb"] >= 16:
                return "medium"
            else:
                return "light"
        
    def _has_npu(self) -> bool:
        """
        Best-effort NPU detection.
        - Honors explicit override via settings.NPU_FORCE_ENABLE
        - Tries OpenVINO device query if openvino.runtime is available
        - Falls back to simple heuristics on CPU/SoC names
        """
        from app.core.config import settings
        if getattr(settings, "NPU_FORCE_ENABLE", False):
            return True
        # Try OpenVINO device query
        try:
            import importlib
            ov = importlib.import_module("openvino.runtime")
            core = ov.Core()
            devices = core.available_devices
            for dev in devices:
                if "NPU" in dev.upper() or "GNA" in dev.upper():
                    return True
        except Exception:
            pass
        # Try onnxruntime accelerators for NPU-like devices
        try:
            providers = self._get_runtime_providers()
            if any('NpuExecutionProvider' in p for p in providers):
                return True
        except Exception:
            pass
        # Simple CPU/SoC heuristic
        architecture = self.cpu_info.get("architecture", "").lower()
        cpu_vendor_str = platform.processor().lower()
        hints = ["neural", "npu", "ai engine", "ai boost", "hexagon"]
        if any(h in cpu_vendor_str for h in hints) or "npu" in architecture:
            return True
        return False
        
    def _check_vendor_npu(self) -> bool:
        """
        Deprecated: retained for backward compatibility; handled in _has_npu.
        """
        return self._has_npu()
                
    def _get_runtime_providers(self) -> Optional[List[str]]:
        """Return available onnxruntime execution providers if onnxruntime is installed."""
        try:
            import onnxruntime as ort
            return list(getattr(ort, 'get_available_providers', lambda: [])()) or list(getattr(ort, 'get_available_providers', []))
        except Exception:
            return []

    def get_capabilities(self) -> Dict:
        """Get full hardware capabilities"""
        return {
            "cpu": self.cpu_info,
            "gpu": self.gpu_info,
            "memory": self.memory_info,
            "acceleration_providers": self.accel_providers,
            "profile": self.get_hardware_profile()
        }

# Example usage
if __name__ == "__main__":
    detector = HardwareDetector()
    print(detector.get_capabilities())
