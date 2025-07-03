"""
Pydantic models for request/response validation
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class OCRRequest(BaseModel):
    """Request model for OCR processing"""
    model: str = Field(default="gemini-2.5-flash", description="AI model to use for OCR")
    language: str = Field(default="en", description="Expected language in the document")
    
class OCRResponse(BaseModel):
    """Response model for OCR processing"""
    text: str = Field(description="Extracted text content")
    confidence: float = Field(description="Confidence score (0-1)", ge=0, le=1)
    metadata: Dict[str, Any] = Field(description="Processing metadata")
    processing_time_ms: int = Field(description="Processing time in milliseconds")
    
class OCRMetadata(BaseModel):
    """Metadata for OCR processing"""
    model: str
    api_key_name: str
    language: str
    filename: str
    file_type: str
    file_size: int
    pages: int = 1
    words: int
    characters: int
    timestamp: datetime

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: datetime = Field(description="Current server timestamp")
    api_keys_status: Dict[str, Any] = Field(description="API key statistics")
    uptime_seconds: int = Field(description="Server uptime in seconds")

class ModelInfo(BaseModel):
    """Information about available models"""
    id: str = Field(description="Model identifier")
    name: str = Field(description="Human-readable model name")
    provider: str = Field(description="Model provider (e.g., 'google')")
    description: str = Field(description="Model description")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(description="Error message")
    details: Optional[str] = Field(description="Additional error details")
    timestamp: datetime = Field(description="Error timestamp")
    
class FileValidationError(BaseModel):
    """File validation error details"""
    filename: str
    error_type: str
    message: str
    max_size_mb: Optional[float] = None
    allowed_extensions: Optional[List[str]] = None 