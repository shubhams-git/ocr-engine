from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class OCRResponse(BaseModel):
    """OCR processing response"""
    success: bool = Field(..., description="Processing success status")
    data: str = Field(..., description="Extracted JSON data")
    error: Optional[str] = Field(None, description="Error message if processing failed")

class MultiPDFAnalysisResponse(BaseModel):
    """Multi-PDF analysis response with projections"""
    success: bool = Field(..., description="Processing success status")
    extracted_data: List[dict] = Field(..., description="Extracted data from each PDF")
    normalized_data: dict = Field(..., description="Normalized and combined data")
    projections: dict = Field(..., description="Projections based on the data")
    explanation: str = Field(..., description="Explanation of calculations and methodology")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    
    # Enhanced fields for better projection analysis (optional for backward compatibility)
    data_quality_score: Optional[float] = Field(None, description="Data completeness and quality score (0-1)")
    confidence_levels: Optional[Dict[str, str]] = Field(None, description="Confidence levels by projection year")
    assumptions: Optional[List[str]] = Field(None, description="List of key assumptions used")
    risk_factors: Optional[List[str]] = Field(None, description="Identified risk factors")
    methodology: Optional[str] = Field(None, description="Forecasting methodology used")
    scenarios: Optional[Dict[str, Any]] = Field(None, description="Alternative scenarios (optimistic/conservative)")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code") 