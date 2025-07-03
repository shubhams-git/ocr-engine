from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ModelProvider(str, Enum):
    """Available AI model providers"""
    GOOGLE = "Google"

class FileFormat(BaseModel):
    """File format specification"""
    extension: str = Field(..., description="File extension")
    mime_type: str = Field(..., description="MIME type") 
    max_size_mb: int = Field(..., description="Maximum file size in MB")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "extension": "png",
                "mime_type": "image/png",
                "max_size_mb": 10
            }
        }
    }

class AIModel(BaseModel):
    """AI model information"""
    id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Human-readable model name")
    provider: ModelProvider = Field(..., description="Model provider")
    description: str = Field(..., description="Model description")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "provider": "Google",
                "description": "Fast model for quick processing"
            }
        }
    }

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: float = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    api_keys_status: str = Field(..., description="API keys availability status")

class ModelsResponse(BaseModel):
    """Available models response"""
    models: List[AIModel] = Field(..., description="List of available AI models")
    default: str = Field(..., description="Default model ID")
    total_count: int = Field(..., description="Total number of models")

class SupportedFormatsResponse(BaseModel):
    """Supported file formats response"""
    image_formats: List[FileFormat] = Field(..., description="Supported image formats")
    document_formats: List[FileFormat] = Field(..., description="Supported document formats")
    max_file_size: Dict[str, str] = Field(..., description="Maximum file sizes by category")

class PromptResponse(BaseModel):
    """OCR prompt information"""
    prompt: str = Field(..., description="Current OCR prompt text")
    length: int = Field(..., description="Prompt length in characters")
    last_modified: str = Field(..., description="Last modification timestamp")

class APIStats(BaseModel):
    """API usage statistics"""
    uptime_seconds: int = Field(..., description="Uptime in seconds")
    uptime_formatted: str = Field(..., description="Human-readable uptime")
    requests_total: int = Field(..., description="Total requests processed")
    requests_successful: int = Field(..., description="Successful requests")
    requests_failed: int = Field(..., description="Failed requests")
    success_rate: float = Field(..., description="Success rate percentage")
    available_api_keys: int = Field(..., description="Number of available API keys")

class OCRMetadata(BaseModel):
    """OCR processing metadata"""
    model_used: str = Field(..., description="AI model used for processing")
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="File MIME type")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    text_length: int = Field(..., description="Extracted text length")
    timestamp: float = Field(..., description="Processing timestamp")

class OCRResponse(BaseModel):
    """OCR processing response"""
    success: bool = Field(..., description="Processing success status")
    text: str = Field(..., description="Extracted text content")
    confidence: float = Field(..., description="Extraction confidence score", ge=0, le=1)
    metadata: OCRMetadata = Field(..., description="Processing metadata")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")

class OCRRequest(BaseModel):
    """OCR processing request parameters"""
    model: Optional[str] = Field("gemini-1.5-flash", description="AI model to use")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: Optional[float] = Field(None, description="Error timestamp")

class RootResponse(BaseModel):
    """Root endpoint response"""
    message: str = Field(..., description="Welcome message")
    version: str = Field(..., description="API version") 