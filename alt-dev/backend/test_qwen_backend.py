#!/usr/bin/env python3
"""
Comprehensive test script for QwenAssistant backend with database integration
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("TESTING BACKEND IMPORTS")
    print("=" * 60)
    try:
        import app.main
        print("✓ Backend main application imported successfully")

        import app.models.database
        print("✓ Database models imported successfully")

        import app.services.hardware_detector
        import app.services.model_router
        import app.services.memory_service
        import app.services.voice_service
        import app.services.privacy_service
        import app.services.vector_store
        import app.services.embedding_service
        print("✓ All services imported successfully")

        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_initialization():
    """Test database initialization and operations"""
    print("\n" + "=" * 60)
    print("TESTING DATABASE INITIALIZATION")
    print("=" * 60)
    try:
        from app.models.database import db, Conversation, Message
        print("✓ Database module imported successfully")

        # Test conversation creation
        conv = db.create_conversation("Test Conversation")
        print(f"✓ Created conversation: {conv.id}")

        # Test message creation
        msg = db.add_message(conv.id, "user", "Hello, assistant!")
        print(f"✓ Added message: {msg.id}")

        # Test conversation retrieval
        retrieved_conv = db.get_conversation(conv.id)
        if retrieved_conv and retrieved_conv.id == conv.id:
            print(f"✓ Retrieved conversation successfully")
        else:
            print(f"✗ Failed to retrieve conversation")
            return False

        # Test messages retrieval
        messages = db.get_messages(conv.id)
        if len(messages) > 0:
            print(f"✓ Retrieved {len(messages)} message(s)")
        else:
            print(f"✗ No messages retrieved")
            return False

        # Test get conversations list
        all_convs = db.get_conversations()
        print(f"✓ Retrieved {len(all_convs)} total conversation(s)")

        return True
    except Exception as e:
        print(f"✗ Database test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hardware_detection():
    """Test hardware detection"""
    print("\n" + "=" * 60)
    print("TESTING HARDWARE DETECTION")
    print("=" * 60)
    try:
        from app.services.hardware_detector import HardwareDetector
        detector = HardwareDetector()
        capabilities = detector.get_capabilities()
        print(f"✓ Hardware detection works")
        print(f"  - Profile: {capabilities['profile']}")
        print(f"  - CPU Cores: {capabilities['cpu']['cores']}")
        print(f"  - Memory: {capabilities['memory']['total_gb']}GB")
        if capabilities['gpu']:
            print(f"  - GPU: {capabilities['gpu']['name']} ({capabilities['gpu']['memory_gb']}GB)")
        return True
    except Exception as e:
        print(f"✗ Hardware detection error: {e}")
        return False

def test_privacy_service():
    """Test privacy service"""
    print("\n" + "=" * 60)
    print("TESTING PRIVACY SERVICE")
    print("=" * 60)
    try:
        from app.services.privacy_service import privacy_service

        # Test classification
        test_email = "test@example.com"
        classification = privacy_service.classify_data(test_email)
        print(f"✓ Data classification works: '{test_email}' -> {classification.value}")

        # Test encryption/decryption
        plaintext = "This is sensitive data"
        encrypted = privacy_service.encrypt_data(plaintext)
        decrypted = privacy_service.decrypt_data(encrypted)
        if decrypted == plaintext:
            print(f"✓ Encryption/decryption works correctly")
        else:
            print(f"✗ Encryption/decryption failed")
            return False

        # Test redaction
        ssn = "123-45-6789"
        redacted = privacy_service.redact_sensitive_data(ssn)
        if "[SSN_REDACTED]" in redacted:
            print(f"✓ Data redaction works: SSN redacted")
        else:
            print(f"✗ Data redaction failed")
            return False

        return True
    except Exception as e:
        print(f"✗ Privacy service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_service():
    """Test memory service with database"""
    print("\n" + "=" * 60)
    print("TESTING MEMORY SERVICE")
    print("=" * 60)
    try:
        from app.services.memory_service import memory_service

        # Test conversation storage
        conv = memory_service.store_conversation("Memory Test Conversation")
        print(f"✓ Stored conversation: {conv.id}")

        # Test message addition
        msg = memory_service.add_message(conv.id, "user", "Test message for memory")
        print(f"✓ Added message to memory: {msg.id}")

        # Test retrieval
        retrieved_msg = memory_service.get_messages(conv.id)
        if len(retrieved_msg) > 0:
            print(f"✓ Retrieved {len(retrieved_msg)} message(s) from memory")
        else:
            print(f"✗ Failed to retrieve messages from memory")
            return False

        return True
    except Exception as e:
        print(f"✗ Memory service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedding_service():
    """Test embedding service"""
    print("\n" + "=" * 60)
    print("TESTING EMBEDDING SERVICE")
    print("=" * 60)
    try:
        from app.services.embedding_service import embedding_service
        import numpy as np

        texts = ["Hello world", "How are you?"]
        embeddings = embedding_service.embed_texts(texts)

        if embeddings.shape == (2, 768):
            print(f"✓ Embedding service works: {embeddings.shape}")
            print(f"  - Generated embeddings with shape {embeddings.shape}")
            print(f"  - L2 norms: {np.linalg.norm(embeddings, axis=1)}")
        else:
            print(f"✗ Unexpected embedding shape: {embeddings.shape}")
            return False

        return True
    except Exception as e:
        print(f"✗ Embedding service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + "  QWENASSISTANT BACKEND COMPREHENSIVE TEST SUITE  ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")

    tests = [
        ("Imports", test_imports),
        ("Database", test_database_initialization),
        ("Hardware Detection", test_hardware_detection),
        ("Privacy Service", test_privacy_service),
        ("Memory Service", test_memory_service),
        ("Embedding Service", test_embedding_service),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"✗ Unexpected error in {name}: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {name}")

    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n✓ All tests passed! QwenAssistant backend is ready to use.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
