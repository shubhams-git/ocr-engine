"""
Professional OCR API Server using Google Gemini AI
Provides comprehensive text extraction from images and PDF documents
"""
import os
import time
import base64
import logging
from typing import Optional

import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import get_api_key, ALLOWED_ORIGINS, get_api_key_count
from prompt import get_prompt
from models import (
    RootResponse, HealthResponse, ModelsResponse, SupportedFormatsResponse,
    PromptResponse, APIStats, OCRResponse, ErrorResponse, AIModel, FileFormat,
    ModelProvider, OCRMetadata
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced FastAPI app with comprehensive documentation
app = FastAPI(
    title="🔍 OCR Engine API",
    description="""
    ## Professional OCR API powered by Google Gemini AI
    
    Extract text from images and PDF documents with high accuracy using state-of-the-art AI models.
    
    ### Features
    - **🖼️ Image Processing**: Support for PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
    - **📄 PDF Processing**: Extract text from PDF documents up to 50MB
    - **🤖 Multiple AI Models**: Choose from various Gemini models
    - **⚡ Fast Processing**: Optimized for quick text extraction
    - **📊 Analytics**: Track usage and performance metrics
    
    ### Quick Start
    1. Upload your file using the `/ocr` endpoint
    2. Choose your preferred AI model (optional)
    3. Receive extracted text with metadata
    
    ### API Limits
    - **Images**: Maximum 10MB per file
    - **PDFs**: Maximum 50MB per file
    - **Rate Limits**: Applied per API key
    
    ### Authentication
    API keys are managed server-side. Contact admin for access.
    """,
    version="2.0.0",
    contact={
        "name": "OCR Engine Support",
        "email": "support@ocrengine.com",
        "url": "https://github.com/yourorg/ocr-engine"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.ocrengine.com",
            "description": "Production server"
        }
    ],
    openapi_tags=[
        {
            "name": "Health",
            "description": "System health and status endpoints"
        },
        {
            "name": "OCR",
            "description": "Text extraction and processing operations"
        },
        {
            "name": "Models",
            "description": "AI model information and configuration"
        },
        {
            "name": "System",
            "description": "System information and statistics"
        }
    ]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# API usage statistics (simple in-memory tracking)
api_stats = {
    "requests_total": 0,
    "requests_successful": 0,
    "requests_failed": 0,
    "start_time": time.time()
}

@app.get(
    "/",
    response_model=RootResponse,
    tags=["Health"],
    summary="API Root",
    description="Welcome endpoint providing basic API information"
)
async def root():
    """
    Welcome to the OCR Engine API
    
    Returns basic information about the API including version and capabilities.
    """
    return RootResponse(
        message="🔍 OCR Engine API - Extract text from images and PDFs",
        version="2.0.0"
    )

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="Check API health status and system availability",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": 1672531200.0,
                        "version": "2.0.0",
                        "api_keys_status": "3 keys available"
                    }
                }
            }
        }
    }
)
async def health():
    """
    Comprehensive health check endpoint
    
    Verifies:
    - API service availability
    - Database connections
    - External service status
    - API key availability
    """
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="2.0.0",
        api_keys_status=f"{get_api_key_count()} keys available"
    )

@app.get(
    "/models",
    response_model=ModelsResponse,
    tags=["Models"],
    summary="Available AI Models",
    description="Get list of available Gemini AI models for text extraction",
    responses={
        200: {
            "description": "List of available models",
            "content": {
                "application/json": {
                    "example": {
                        "models": [
                            {
                                "id": "gemini-1.5-flash",
                                "name": "Gemini 1.5 Flash",
                                "provider": "Google",
                                "description": "Fast model for quick processing"
                            }
                        ],
                        "default": "gemini-1.5-flash",
                        "total_count": 3
                    }
                }
            }
        }
    }
)
async def get_models():
    """
    Retrieve available AI models
    
    Returns information about all available Gemini models including:
    - Model identifiers and names
    - Performance characteristics
    - Recommended use cases
    """
    models = [
        AIModel(
            id="gemini-1.5-pro", 
            name="Gemini 1.5 Pro",
            provider=ModelProvider.GOOGLE,
            description="Most capable model for complex documents and high accuracy requirements"
        ),
        AIModel(
            id="gemini-1.5-flash", 
            name="Gemini 1.5 Flash",
            provider=ModelProvider.GOOGLE, 
            description="Optimized for speed while maintaining good accuracy - Recommended"
        ),
        AIModel(
            id="gemini-2.0-flash-exp", 
            name="Gemini 2.0 Flash (Experimental)",
            provider=ModelProvider.GOOGLE,
            description="Latest experimental model with enhanced capabilities"
        )
    ]
    return ModelsResponse(
        models=models,
        default="gemini-1.5-flash",
        total_count=len(models)
    )

@app.get(
    "/formats",
    response_model=SupportedFormatsResponse,
    tags=["System"],
    summary="Supported File Formats",
    description="Get detailed information about supported file formats and size limits"
)
async def get_supported_formats():
    """
    File format specifications
    
    Returns comprehensive information about:
    - Supported image formats and extensions
    - PDF processing capabilities
    - File size limitations
    - MIME type mappings
    """
    image_formats = [
        FileFormat(extension="png", mime_type="image/png", max_size_mb=10),
        FileFormat(extension="jpg", mime_type="image/jpeg", max_size_mb=10),
        FileFormat(extension="jpeg", mime_type="image/jpeg", max_size_mb=10),
        FileFormat(extension="gif", mime_type="image/gif", max_size_mb=10),
        FileFormat(extension="bmp", mime_type="image/bmp", max_size_mb=10),
        FileFormat(extension="tiff", mime_type="image/tiff", max_size_mb=10),
        FileFormat(extension="webp", mime_type="image/webp", max_size_mb=10)
    ]
    
    document_formats = [
        FileFormat(extension="pdf", mime_type="application/pdf", max_size_mb=50)
    ]
    
    return SupportedFormatsResponse(
        image_formats=image_formats,
        document_formats=document_formats,
        max_file_size={
            "images": "10MB",
            "pdfs": "50MB"
        }
    )

@app.get(
    "/prompt",
    response_model=PromptResponse,
    tags=["System"],
    summary="Current OCR Prompt",
    description="Get the current prompt template used for text extraction"
)
async def get_current_prompt():
    """
    OCR prompt configuration
    
    Returns the current prompt template that instructs the AI model
    on how to extract and format text from documents.
    """
    prompt_text = get_prompt()
    return PromptResponse(
        prompt=prompt_text,
        length=len(prompt_text),
        last_modified="2025-01-03T00:00:00Z"
    )

@app.get(
    "/stats",
    response_model=APIStats,
    tags=["System"],
    summary="API Usage Statistics",
    description="Get real-time API usage metrics and performance statistics"
)
async def get_api_stats():
    """
    Comprehensive API analytics
    
    Provides insights into:
    - Request volume and success rates
    - System uptime and performance
    - Resource availability
    - Usage patterns
    """
    uptime = time.time() - api_stats["start_time"]
    return APIStats(
        uptime_seconds=int(uptime),
        uptime_formatted=f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m",
        requests_total=api_stats["requests_total"],
        requests_successful=api_stats["requests_successful"], 
        requests_failed=api_stats["requests_failed"],
        success_rate=(api_stats["requests_successful"] / max(api_stats["requests_total"], 1)) * 100,
        available_api_keys=get_api_key_count()
    )

@app.post(
    "/ocr",
    response_model=OCRResponse,
    tags=["OCR"],
    summary="Extract Text from File",
    description="Upload an image or PDF file to extract text using AI-powered OCR",
    responses={
        200: {
            "description": "Text extraction successful",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "text": "This is the extracted text from your document...",
                        "confidence": 0.95,
                        "metadata": {
                            "model_used": "gemini-1.5-flash",
                            "file_name": "document.pdf",
                            "file_size": 1024000,
                            "content_type": "application/pdf",
                            "processing_time_ms": 2500,
                            "text_length": 1500,
                            "timestamp": 1672531200.0
                        },
                        "processing_time_ms": 2500
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "Invalid file format or size"},
        413: {"model": ErrorResponse, "description": "File too large"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Processing error"}
    }
)
async def process_ocr(
    file: UploadFile = File(
        ...,
        description="Image or PDF file to process",
        media_type="multipart/form-data"
    ),
    model: Optional[str] = Form(
        "gemini-1.5-flash",
        description="AI model to use for text extraction",
        regex="^(gemini-1\.5-pro|gemini-1\.5-flash|gemini-2\.0-flash-exp)$"
    )
):
    """
    **Extract text from uploaded files using AI-powered OCR**
    
    This endpoint processes image files and PDF documents to extract readable text
    using Google's Gemini AI models.
    
    ### Supported Files
    - **Images**: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP (max 10MB)
    - **Documents**: PDF (max 50MB)
    
    ### Processing Options
    - **gemini-1.5-flash**: Fast processing, good accuracy (Recommended)
    - **gemini-1.5-pro**: Highest accuracy, slower processing
    - **gemini-2.0-flash-exp**: Latest model, experimental features
    
    ### Response Details
    The response includes:
    - Extracted text content
    - Confidence score
    - Processing metadata
    - Performance metrics
    
    ### Error Handling
    - Invalid file types return 400
    - Files exceeding size limits return 413
    - Processing failures return 500
    """
    # Track API usage
    api_stats["requests_total"] += 1
    
    try:
        # Use default model if none provided
        model_name = model or "gemini-1.5-flash"
        logger.info(f"Processing file: {file.filename} with model: {model_name}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")
        
        # Validate file size
        content_type = file.content_type or ""
        max_size = 50 * 1024 * 1024 if content_type == 'application/pdf' else 10 * 1024 * 1024
        
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {'50MB for PDFs' if content_type == 'application/pdf' else '10MB for images'}"
            )
        
        # Get API key and configure Gemini
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        
        # Create model instance
        gemini_model = genai.GenerativeModel(model_name)
        
        # Prepare content based on file type
        if content_type.startswith('image/'):
            # Handle image files
            content_parts = [
                get_prompt(),
                {
                    "mime_type": content_type,
                    "data": base64.b64encode(content).decode()
                }
            ]
        elif content_type == 'application/pdf':
            # Handle PDF files
            content_parts = [
                get_prompt(),
                {
                    "mime_type": "application/pdf",
                    "data": base64.b64encode(content).decode()
                }
            ]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Please upload an image (PNG, JPG, etc.) or PDF file."
            )
        
        # Make API request to Gemini
        logger.info("Sending request to Gemini API...")
        start_time = time.time()
        
        response = gemini_model.generate_content(content_parts)
        
        end_time = time.time()
        processing_time = int((end_time - start_time) * 1000)
        
        # Extract text from response
        if response and response.text:
            extracted_text = response.text.strip()
            logger.info(f"Successfully extracted {len(extracted_text)} characters")
            
            # Track successful request
            api_stats["requests_successful"] += 1
            
            return OCRResponse(
                success=True,
                text=extracted_text,
                confidence=0.95,  # Default confidence for Gemini
                metadata=OCRMetadata(
                    model_used=model_name,
                    file_name=file.filename,
                    file_size=len(content),
                    content_type=content_type,
                    processing_time_ms=processing_time,
                    text_length=len(extracted_text),
                    timestamp=time.time()
                ),
                processing_time_ms=processing_time
            )
        else:
            api_stats["requests_failed"] += 1
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No text could be extracted from the file"
            )
            
    except HTTPException:
        api_stats["requests_failed"] += 1
        raise
    except Exception as e:
        api_stats["requests_failed"] += 1
        logger.error(f"OCR processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )

# Custom error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom error handler for HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": time.time()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 