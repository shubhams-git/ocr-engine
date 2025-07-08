"""
Multi-PDF analysis endpoints
"""
import logging
from typing import List
from fastapi import APIRouter, File, UploadFile, Form
from models import MultiPDFAnalysisResponse
from services.multi_pdf_service import multi_pdf_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/multi-pdf", tags=["multi-pdf"])

@router.post("/analyze", response_model=MultiPDFAnalysisResponse)
async def analyze_multiple_pdfs(
    files: List[UploadFile] = File(...), 
    model: str = Form(default="gemini-2.5-flash")
):
    """
    Analyze multiple PDF files with data extraction, normalization, and projections
    
    - **files**: List of PDF files to analyze (max 10 files, 50MB each)
    - **model**: Gemini model to use for analysis (default: gemini-2.5-flash)
    
    Returns comprehensive analysis with:
    - Extracted data from each document
    - Normalized and combined data
    - Projections and insights
    - Detailed explanations
    """
    logger.info(f"Starting multi-PDF analysis for {len(files)} files with model: {model}")
    
    # Read all file contents
    files_data = []
    for file in files:
        content = await file.read()
        files_data.append((file.filename or "unknown.pdf", content))
    
    # Process using the multi-PDF service
    result = await multi_pdf_service.analyze_multiple_pdfs(files_data, model)
    
    logger.info(f"Multi-PDF analysis completed. Success: {result.success}")
    return result 