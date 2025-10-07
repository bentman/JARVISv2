#!/usr/bin/env python3
\"\"\"
Test script to verify the backend can start without errors
\"\"\"
import sys
import os

def test_backend_startup():
    \"\"\"Test that the backend can be imported and started without errors\"\"\"
    try:
        # Add the app directory to the Python path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        app_path = os.path.join(backend_path, 'app')
        sys.path.insert(0, app_path)
        
        # Try importing the main application
        from app.main import app
        print(\"✓ Backend main application imported successfully\")
        
        # Try importing key components
        from app.services.hardware_detector import HardwareDetector
        from app.services.model_router import ModelRouter
        from app.services.memory_service import memory_service
        from app.services.voice_service import voice_service
        from app.services.privacy_service import privacy_service
        
        print(\"✓ All services imported successfully\")
        
        # Test hardware detection
        detector = HardwareDetector()
        capabilities = detector.get_capabilities()
        print(f\"✓ Hardware detection works, profile: {capabilities['profile']}\")
        
        # Test privacy service
        result = privacy_service.enforce_local_processing(\"This is a test message\")
        print(f\"✓ Privacy service works, classification: {result['classification']}\")
        
        print(\"\\n✓ All backend components work correctly!\")
        return True
        
    except Exception as e:
        print(f\"✗ Error testing backend: {e}\")
        import traceback
        traceback.print_exc()
        return False

if __name__ == \"__main__\":
    success = test_backend_startup()
    if not success:
        sys.exit(1)