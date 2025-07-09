"""
OCR processing endpoints
"""
import logging
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from models import OCRResponse
from services.ocr_service import ocr_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ocr"])

@router.post("/ocr", response_model=OCRResponse)
async def process_ocr(
    file: UploadFile = File(...), 
    model: str = Form(default="gemini-2.5-flash")
):
    """Extract data from uploaded image, PDF, or CSV file using Gemini AI with API key rotation"""
    logger.info(f"Starting OCR processing for file: {file.filename} with model: {model}")
    
    # Validate that we have a file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Log file details for debugging
    file_extension = Path(file.filename).suffix.lower()
    logger.info(f"File extension: {file_extension}, Content type: {file.content_type}")
    
    try:
        # Read file content
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")
        
        # Process using the OCR service
        result = await ocr_service.process_ocr(content, file.filename, model)
        
        logger.info(f"OCR processing completed. Success: {result.success}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during OCR processing: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error during file processing: {str(e)}"
        ) 