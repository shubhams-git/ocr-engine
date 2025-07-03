#!/usr/bin/env python3
"""
Simple server startup script for Windows
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting OCR Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Try running in Windows Command Prompt instead of Git Bash") 