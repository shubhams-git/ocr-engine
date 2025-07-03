"""
Main FastAPI application for OCR Engine Backend
"""
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings, api_manager
from .models import OCRResponse, HealthResponse, ModelInfo, ErrorResponse
from .services.ocr_service import ocr_service
from . import __version__

logger = logging.getLogger(__name__)

# FastAPI app instance
app = FastAPI(
    title="OCR Engine API",
    description="AI-powered OCR service using Google Gemini API with automatic key rotation",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Track startup time for uptime calculation
startup_time = time.time()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with detailed logging"""
    logger.error(f"🚫 HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            details=None,
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle request validation errors"""
    logger.error(f"🚫 Validation Error: {exc}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Request validation failed",
            details=str(exc),
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"💥 Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            details=str(exc) if settings.DEBUG else "An unexpected error occurred",
            timestamp=datetime.now()
        ).dict()
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Get client info
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    logger.info(f"🌐 {request.method} {request.url.path} - Client: {client_ip}")
    
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log response
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with service status"""
    logger.info("🏥 Health check requested")
    
    try:
        health_info = ocr_service.get_service_health()
        uptime_seconds = int(time.time() - startup_time)
        
        return HealthResponse(
            status=health_info["status"],
            version=__version__,
            timestamp=datetime.now(),
            api_keys_status=api_manager.get_key_stats(),
            uptime_seconds=uptime_seconds
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Models endpoint
@app.get("/api/models", response_model=Dict[str, Any])
async def get_models():
    """Get available AI models"""
    logger.info("🤖 Models list requested")
    
    try:
        models_info = ocr_service.get_available_models()
        return {
            "models": models_info["models"],
            "default": models_info["default"],
            "recommended": models_info["recommended"],
            "total_count": len(models_info["models"])
        }
    except Exception as e:
        logger.error(f"❌ Failed to get models: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")

# Supported formats endpoint
@app.get("/api/formats", response_model=Dict[str, Any])
async def get_supported_formats():
    """Get supported file formats"""
    logger.info("📋 Supported formats requested")
    
    try:
        formats = ocr_service.get_supported_formats()
        return {
            "supported_formats": formats,
            "total_types": len(formats["images"]["mime_types"] + formats["documents"]["mime_types"])
        }
    except Exception as e:
        logger.error(f"❌ Failed to get formats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve formats")

# Main OCR processing endpoint
@app.post("/api/ocr/process", response_model=OCRResponse)
async def process_ocr(
    file: UploadFile = File(..., description="File to process (image or PDF)"),
    model: Optional[str] = Form(default="gemini-2.5-flash", description="AI model to use"),
    language: Optional[str] = Form(default="en", description="Expected language in document")
):
    """
    Process uploaded file for OCR text extraction
    
    - **file**: Image or PDF file to process
    - **model**: AI model to use (default: gemini-2.5-flash)
    - **language**: Expected language code (default: en)
    """
    logger.info(f"📝 OCR processing requested: {file.filename} (model: {model}, language: {language})")
    
    try:
        # Process the file with default values for None parameters
        model_to_use = model or "gemini-2.5-flash"
        language_to_use = language or "en"
        result = await ocr_service.process_file(file, model_to_use, language_to_use)
        
        logger.info(f"✅ OCR processing successful: {file.filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 OCR processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

# API statistics endpoint
@app.get("/api/stats", response_model=Dict[str, Any])
async def get_api_stats():
    """Get API usage statistics"""
    logger.info("📊 API statistics requested")
    
    try:
        uptime_seconds = int(time.time() - startup_time)
        
        return {
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s",
            "api_keys": api_manager.get_key_stats(),
            "service_health": ocr_service.get_service_health(),
            "version": __version__,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "OCR Engine API",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/health",
        "models": "/api/models",
        "process": "/api/ocr/process"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Starting OCR Engine API")
    logger.info(f"📍 Version: {__version__}")
    logger.info(f"🌐 CORS origins: {settings.ALLOWED_ORIGINS}")
    logger.info(f"📁 Max file size: {settings.MAX_FILE_SIZE / (1024 * 1024):.1f}MB")
    logger.info(f"🔑 API keys available: {len(api_manager.api_keys)}")
    logger.info("✅ OCR Engine API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    uptime = int(time.time() - startup_time)
    logger.info(f"🛑 Shutting down OCR Engine API (uptime: {uptime}s)")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 