import psutil
import GPUtil
import platform
from typing import Dict, Optional

class HardwareDetector:
    """
    Detects hardware capabilities and determines appropriate profile
    """
    
    def __init__(self):
        self.cpu_info = self._get_cpu_info()
        self.gpu_info = self._get_gpu_info()
        self.memory_info = self._get_memory_info()
        
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
        
        # Check for GPU
        if self.gpu_info and self.gpu_info["memory_gb"] >= 8:
            # Check if we have enough total memory to run large models alongside other processes
            if self.memory_info["total_gb"] >= 16:
                return "heavy"
            else:
                return "medium"
        elif self.gpu_info and self.gpu_info["memory_gb"] >= 4:
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
            # Common OpenVINO logical device names include: CPU, GPU, NPU, GNA, AUTO, etc.
            for dev in devices:
                if "NPU" in dev.upper() or "GNA" in dev.upper():
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
                
    def get_capabilities(self) -> Dict:
        """Get full hardware capabilities"""
        return {
            "cpu": self.cpu_info,
            "gpu": self.gpu_info,
            "memory": self.memory_info,
            "profile": self.get_hardware_profile()
        }

# Example usage
if __name__ == "__main__":
    detector = HardwareDetector()
    print(detector.get_capabilities())
