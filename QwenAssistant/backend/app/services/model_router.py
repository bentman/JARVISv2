import os
import subprocess
import sys
from typing import Dict, List, Generator, Optional
from app.core.config import settings
from pydantic import BaseModel
from pathlib import Path


class ModelInferenceResult(BaseModel):
    """Result from model inference"""
    response: str
    tokens_used: int
    execution_time: float


class ModelRouter:
    """
    Routes requests to appropriate models based on hardware profile and task type
    Uses llama.cpp for GGUF model execution
    """
    
    def __init__(self):
        self.models = self._load_models()
        self.llama_cpp_path = self._find_llama_cpp()
        
    def _find_llama_cpp(self) -> str:
        """Find the llama.cpp executable"""
        # Common paths where llama.cpp might be installed
        possible_paths = [
            "/usr/local/bin/llama",
            "/opt/llama/bin/llama",
            "./llama.cpp/main",  # Local build
            settings.MODEL_PATH + "/llama.cpp/main",  # Model directory
            # Check if it's in system PATH
            "llama",
            "llama-cli",
            "llama-gguf"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        # If not found, try to install llama.cpp
        self._install_llama_cpp()
        return "llama"
    
    def _install_llama_cpp(self):
        """Install llama.cpp if not found"""
        print("Installing llama.cpp...")
        try:
            # Clone the repository
            subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp.git"], check=True)
            os.chdir("llama.cpp")
            # Build llama.cpp
            subprocess.run(["make"], check=True)
            os.chdir("..")
            print("llama.cpp installed successfully")
        except subprocess.CalledProcessError:
            print("Failed to install llama.cpp automatically. Please install manually.")
            raise
    
    def _load_models(self) -> Dict:
        """Load available models from the models directory (recursive) and record file paths"""
        models_path = Path(settings.MODEL_PATH)
        self.model_paths: Dict[str, str] = {}
        available_models = {
            "light": {},
            "medium": {},
            "heavy": {},
            "npu-optimized": {}
        }
        
        # Recursively scan for .gguf files and categorize by filename hints
        if models_path.exists():
            gguf_files = list(models_path.rglob("*.gguf"))
            for file_path in gguf_files:
                filename = file_path.stem
                # Record exact path for retrieval
                self.model_paths[filename] = str(file_path)
                # Simplified categorization based on filename
                if any(tag in filename for tag in ["1b", "2b", "3b"]):
                    available_models["light"].setdefault("chat", filename)
                elif "7b" in filename:
                    available_models["medium"].setdefault("chat", filename)
                elif any(tag in filename for tag in ["13b", "30b", "70b"]):
                    available_models["heavy"].setdefault("chat", filename)
                else:
                    available_models["medium"].setdefault("chat", filename)
        
        # Default fallback models if none found in directory
        if not any(available_models[profile] for profile in available_models):
            available_models = {
                "light": {
                    "chat": "llama-3.2-3b",
                    "coding": "starcoder2-3b",
                    "reasoning": "phi-3-mini-3.8b"
                },
                "medium": {
                    "chat": "mistral-7b-instruct",
                    "coding": "codellama-7b",
                    "reasoning": "mixtral-8x7b"
                },
                "heavy": {
                    "chat": "llama-3.3-70b",
                    "coding": "codellama-13b",
                    "reasoning": "llama-4-maverick-402b"
                },
                "npu-optimized": {
                    "chat": "optimized-phi-3-mini",
                    "coding": "optimized-codellama-7b",
                    "reasoning": "optimized-phi-3-mini"
                }
            }
        
        return available_models
        
    def select_model(self, profile: str, task_type: str) -> str:
        """
        Select appropriate model based on profile and task type
        """
        if profile in self.models and task_type in self.models[profile]:
            return self.models[profile][task_type]
        else:
            # Fallback to chat model
            return self.models[profile].get("chat", "llama-3.2-3b")
            
    def get_model_path(self, model_name: str) -> str:
        """Get path to model file"""
        if hasattr(self, "model_paths") and model_name in self.model_paths:
            return self.model_paths[model_name]
        return os.path.join(settings.MODEL_PATH, f"{model_name}.gguf")
    def get_available_models(self) -> List[str]:
        """Get list of all available models"""
        models = set()
        for profile in self.models.values():
            for model in profile.values():
                models.add(model)
        return list(models)
        
    def get_model_path(self, model_name: str) -> str:
        """Get path to model file"""
        return os.path.join(settings.MODEL_PATH, f"{model_name}.gguf")
    
    def _run_llama_inference(self, model_path: str, prompt: str, max_tokens: int = 256) -> ModelInferenceResult:
        """
        Run inference using llama.cpp
        """
        import time
        start_time = time.time()
        
        try:
            # Prepare the llama.cpp command
            cmd = [
                self.llama_cpp_path,
                "-m", model_path,
                "-p", prompt,
                "-n", str(max_tokens),
                "--temp", "0.7",
                "--repeat-penalty", "1.1"
            ]
            
            # Add hardware-specific optimizations based on available resources
            import psutil
            cpu_count = psutil.cpu_count()
            if cpu_count:
                cmd.extend(["-t", str(max(1, cpu_count // 2))])  # Use half of CPU cores
            
            # Run the llama.cpp command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode != 0:
                raise Exception(f"llama.cpp failed with error: {result.stderr}")
            
            response = result.stdout.strip()
            # Estimate tokens used (simple heuristic)
            tokens_used = len(response.split())
            
            return ModelInferenceResult(
                response=response,
                tokens_used=tokens_used,
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired:
            raise Exception("Model inference timed out")
        except Exception as e:
            raise Exception(f"Error during model inference: {str(e)}")
    
    def generate_response(self, profile: str, task_type: str, prompt: str, max_tokens: int = 256) -> ModelInferenceResult:
        """
        Generate a response from the appropriate model
        """
        model_name = self.select_model(profile, task_type)
        model_path = self.get_model_path(model_name)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        return self._run_llama_inference(model_path, prompt, max_tokens)


# Example usage
if __name__ == "__main__":
    router = ModelRouter()
    print(router.select_model("medium", "coding"))
