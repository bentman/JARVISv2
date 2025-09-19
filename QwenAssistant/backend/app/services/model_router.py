import os
from typing import Dict, List
from app.core.config import settings

class ModelRouter:
    """
    Routes requests to appropriate models based on hardware profile and task type
    """
    
    def __init__(self):
        self.models = self._load_models()
        
    def _load_models(self) -> Dict:
        """Load available models"""
        # In a real implementation, this would scan the models directory
        # and load model metadata
        return {
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
                "coding": "deepseek-coder-33b",
                "reasoning": "llama-4-maverick-402b"
            }
        }
        
    def select_model(self, profile: str, task_type: str) -> str:
        """
        Select appropriate model based on profile and task type
        """
        if profile in self.models and task_type in self.models[profile]:
            return self.models[profile][task_type]
        else:
            # Fallback to chat model
            return self.models[profile].get("chat", "llama-3.2-3b")
            
    def get_available_models(self) -> List[str]:
        """Get list of all available models"""
        models = set()
        for profile in self.models.values():
            for model in profile.values():
                models.add(model)
        return list(models)
        
    def get_model_path(self, model_name: str) -> str:
        """Get path to model file"""
        # In a real implementation, this would return the actual path
        # to the model file in the models directory
        return os.path.join(settings.MODEL_PATH, f"{model_name}.gguf")

# Example usage
if __name__ == "__main__":
    router = ModelRouter()
    print(router.select_model("medium", "coding"))