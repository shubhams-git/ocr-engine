#!/usr/bin/env python3
"""
Environment verification script
Run this after creating your .env file to verify everything is set up correctly
"""
import os
from app.config import api_manager, settings

def verify_environment():
    """Verify environment setup"""
    
    print("🔍 Verifying Environment Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file_exists = os.path.exists('.env')
    if env_file_exists:
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("   Please create a .env file (see env_setup_guide.md)")
        return False
    
    # Check API keys
    stats = api_manager.get_key_stats()
    if stats['total_keys'] > 0 and api_manager.api_keys[0]['key'] != "PLEASE_SET_ENV_VARIABLES":
        print(f"✅ API Keys loaded: {stats['total_keys']} keys")
        
        # Show which keys are loaded (without revealing the actual keys)
        for i, key_info in enumerate(api_manager.api_keys, 1):
            key_preview = key_info['key'][:10] + "..." if len(key_info['key']) > 10 else key_info['key']
            print(f"   {key_info['name']}: {key_preview}")
    else:
        print("❌ No valid API keys found")
        print("   Please add GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc. to your .env file")
        return False
    
    # Check server settings
    print(f"✅ Server Settings: {settings.HOST}:{settings.PORT}")
    
    print("=" * 50)
    print("🎉 Environment verification PASSED!")
    print()
    print("Your backend is ready to run:")
    print("1. pip install -r requirements.txt")
    print("2. python run.py")
    print("3. Visit: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    try:
        verify_environment()
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        print("Make sure you're in the backend directory and have created the .env file") 