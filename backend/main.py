"""
Minimal OCR API Server using Google Gemini AI
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Set up centralized logging first
from logging_config import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)

from config import ALLOWED_ORIGINS
from routers import health, admin, ocr, multi_pdf
from middleware import error_handler

# Create FastAPI app
app = FastAPI(title="OCR API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add simple error handling
app.middleware("http")(error_handler)

# Include routers
app.include_router(health.router)
app.include_router(admin.router)
app.include_router(ocr.router)
app.include_router(multi_pdf.router)

if __name__ == "__main__":
    import uvicorn
    # Set environment variable to indicate we're running as main server
    # This prevents duplicate initialization logs during uvicorn reloads
    os.environ["OCR_SERVER_MAIN"] = "true"
    
    # Configure server with 10-minute timeout
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info",  # Reduce uvicorn startup verbosity
        timeout_keep_alive=600,  # 10 minutes
        timeout_graceful_shutdown=30
    ) 