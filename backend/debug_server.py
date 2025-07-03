#!/usr/bin/env python3
"""
Debug script to test server startup
"""
import sys
import traceback

try:
    print("🔍 Testing imports...")
    from app.main import app
    print("✅ App imported successfully")
    
    print("🔍 Testing uvicorn...")
    import uvicorn
    print(f"✅ Uvicorn version: {uvicorn.__version__}")
    
    print("🚀 Starting server...")
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="info",
        access_log=True
    )
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("📋 Full traceback:")
    traceback.print_exc()
    sys.exit(1) 