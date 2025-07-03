#!/usr/bin/env python3
"""
Startup script for OCR Engine Backend
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("🚀 Starting OCR Engine Backend...")
    print(f"📍 Host: {settings.HOST}")
    print(f"🔌 Port: {settings.PORT}")
    print(f"🐛 Debug: {settings.DEBUG}")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    ) 