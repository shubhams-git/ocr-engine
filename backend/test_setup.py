#!/usr/bin/env python3
"""
Quick test script to validate basic backend setup
"""
from fastapi import FastAPI
from app.config import settings, api_manager

def test_basic_setup():
    """Test basic configuration and imports"""
    
    print("🧪 Testing OCR Engine Backend Setup")
    print("=" * 50)
    
    # Test 1: Configuration
    try:
        print(f"✅ Settings loaded - Host: {settings.HOST}, Port: {settings.PORT}")
    except Exception as e:
        print(f"❌ Settings failed: {e}")
        return False
    
    # Test 2: API Key Manager
    try:
        stats = api_manager.get_key_stats()
        if stats['total_keys'] > 0 and api_manager.api_keys[0]['key'] != "PLEASE_SET_ENV_VARIABLES":
            print(f"✅ API Key Manager - {stats['total_keys']} keys loaded")
        else:
            print(f"⚠️ API Key Manager - No valid keys found!")
            print("   Please create a .env file with your Gemini API keys")
            print("   See env_setup_guide.md for details")
            return False
    except Exception as e:
        print(f"❌ API Key Manager failed: {e}")
        return False
    
    # Test 3: FastAPI Import
    try:
        app = FastAPI(title="OCR Engine Test")
        print("✅ FastAPI imported successfully")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    print("=" * 50)
    print("🎉 Basic setup validation PASSED!")
    print()
    print("Next steps:")
    print("1. Create .env file with your Gemini API keys (see env_setup_guide.md)")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start server: python run.py")
    print("4. Test at: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    test_basic_setup() 