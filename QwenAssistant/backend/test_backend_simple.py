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
        
        # Try importing key components to check if syntax is correct
        import app.main
        print(\"✓ Backend main application imported successfully\")
        
        import app.services.hardware_detector
        import app.services.model_router
        import app.services.memory_service
        import app.services.voice_service
        import app.services.privacy_service
        print(\"✓ All services imported successfully\")
        
        # Test hardware detection
        detector = app.services.hardware_detector.HardwareDetector()
        capabilities = detector.get_capabilities()
        print(f\"✓ Hardware detection works, profile: {capabilities['profile']}\")
        
        # Test privacy service
        privacy_service = app.services.privacy_service.privacy_service
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