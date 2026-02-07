#!/usr/bin/env python3
"""
Quick verification that the QwenAssistant backend structure is complete
"""
import os
import sys
from pathlib import Path

def verify_directory_structure():
    """Verify all required directories exist"""
    print("=" * 60)
    print("VERIFYING DIRECTORY STRUCTURE")
    print("=" * 60)

    required_dirs = [
        "app",
        "app/models",
        "app/core",
        "app/services",
        "app/api",
        "app/api/v1",
        "app/api/v1/endpoints",
        "data",
    ]

    base_path = Path(__file__).parent
    all_exist = True

    for dir_path in required_dirs:
        full_path = base_path / dir_path
        exists = full_path.exists() and full_path.is_dir()
        status = "✓" if exists else "✗"
        print(f"{status} {dir_path}")
        if not exists:
            all_exist = False

    return all_exist

def verify_required_files():
    """Verify all required Python files exist"""
    print("\n" + "=" * 60)
    print("VERIFYING REQUIRED FILES")
    print("=" * 60)

    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/models/__init__.py",
        "app/models/database.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/services/__init__.py",
        "app/services/hardware_detector.py",
        "app/services/model_router.py",
        "app/services/memory_service.py",
        "app/services/voice_service.py",
        "app/services/privacy_service.py",
        "app/services/vector_store.py",
        "app/services/embedding_service.py",
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml" if not Path(__file__).parent.parent.parent.parent.parent / "docker-compose.yml" else "docker-compose.yml"
    ]

    base_path = Path(__file__).parent
    missing_files = []
    all_exist = True

    for file_path in required_files:
        full_path = base_path / file_path
        exists = full_path.exists() and full_path.is_file()
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False
            missing_files.append(file_path)

    return all_exist, missing_files

def verify_database_layer():
    """Verify database.py has required classes"""
    print("\n" + "=" * 60)
    print("VERIFYING DATABASE LAYER")
    print("=" * 60)

    db_path = Path(__file__).parent / "app" / "models" / "database.py"
    if not db_path.exists():
        print("✗ database.py not found")
        return False

    try:
        with open(db_path, 'r') as f:
            content = f.read()

        required_classes = ["Conversation", "Message", "Database"]
        all_found = True

        for cls in required_classes:
            if f"class {cls}" in content:
                print(f"✓ {cls} class defined")
            else:
                print(f"✗ {cls} class NOT found")
                all_found = False

        # Check for required methods
        required_methods = [
            "create_conversation",
            "get_conversations",
            "add_message",
            "get_messages",
            "get_conversation"
        ]

        for method in required_methods:
            if f"def {method}" in content:
                print(f"✓ {method}() method defined")
            else:
                print(f"✗ {method}() method NOT found")
                all_found = False

        return all_found
    except Exception as e:
        print(f"✗ Error reading database.py: {e}")
        return False

def verify_memory_service():
    """Verify memory service imports the database"""
    print("\n" + "=" * 60)
    print("VERIFYING MEMORY SERVICE INTEGRATION")
    print("=" * 60)

    mem_path = Path(__file__).parent / "app" / "services" / "memory_service.py"
    if not mem_path.exists():
        print("✗ memory_service.py not found")
        return False

    try:
        with open(mem_path, 'r') as f:
            content = f.read()

        # Check that database import is present
        if "from app.models.database import" in content:
            print("✓ Imports from app.models.database")
        else:
            print("✗ Does NOT import from app.models.database")
            return False

        # Check for expected classes
        if "class MemoryService" in content:
            print("✓ MemoryService class defined")
        else:
            print("✗ MemoryService class NOT found")
            return False

        return True
    except Exception as e:
        print(f"✗ Error reading memory_service.py: {e}")
        return False

def main():
    """Run all verifications"""
    print("\n╔" + "=" * 58 + "╗")
    print("║" + "  QWENASSISTANT BACKEND STRUCTURE VERIFICATION  ".center(58) + "║")
    print("╚" + "=" * 58 + "╝\n")

    results = {
        "Directory Structure": verify_directory_structure(),
        "Database Layer": verify_database_layer(),
        "Memory Service Integration": verify_memory_service(),
    }

    files_exist, missing = verify_required_files()
    results["Required Files"] = files_exist

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")

    if missing:
        print(f"\nMissing files:")
        for f in missing:
            print(f"  - {f}")

    print("=" * 60)
    print(f"Total: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n✓ QwenAssistant backend structure is COMPLETE and READY!")
        print("  Database layer is properly integrated.")
        print("  Run 'npm install && npm run dev' in frontend directory to start.")
        return 0
    else:
        print(f"\n✗ {total - passed} verification(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
