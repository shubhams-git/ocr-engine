"""
Multi-document analysis endpoints
"""
import logging
from typing import List
from fastapi import APIRouter, File, UploadFile, Form
from models import MultiPDFAnalysisResponse
from services.multi_pdf_service import multi_pdf_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/multi-pdf", tags=["multi-pdf"])

@router.post("/analyze", response_model=MultiPDFAnalysisResponse)
async def analyze_multiple_files(
    files: List[UploadFile] = File(...), 
    model: str = Form(default="gemini-2.5-flash")
):
    """
    Analyze multiple PDF and CSV files with data extraction, normalization, and projections
    
    - **files**: List of PDF and/or CSV files to analyze (max 10 files, 50MB each for PDFs, 25MB each for CSVs)
    - **model**: Gemini model to use for analysis (default: gemini-2.5-flash)
    
    Supported file types:
    - PDF documents (financial statements, reports, etc.)
    - CSV files (financial data in tabular format)
    
    Returns comprehensive analysis with:
    - Extracted data from each document
    - Normalized and combined data
    - Projections and insights
    - Detailed explanations
    """
    logger.info(f"Starting multi-file analysis for {len(files)} files with model: {model}")
    
    # Read all file contents
    files_data = []
    for file in files:
        content = await file.read()
        files_data.append((file.filename or "unknown", content))
    
    # Process using the multi-file service
    result = await multi_pdf_service.analyze_multiple_files(files_data, model)
    
    logger.info(f"Multi-file analysis completed. Success: {result.success}")
    return result 