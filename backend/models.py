from typing import Optional
from pydantic import BaseModel, Field

class OCRResponse(BaseModel):
    """OCR processing response"""
    success: bool = Field(..., description="Processing success status")
    data: str = Field(..., description="Extracted JSON data")
    error: Optional[str] = Field(None, description="Error message if processing failed")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code") 