"""
OCR processing endpoints
"""
import logging
from fastapi import APIRouter, File, UploadFile
from models import OCRResponse
from services.ocr_service import ocr_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ocr"])

@router.post("/ocr", response_model=OCRResponse)
async def process_ocr(file: UploadFile = File(...), model: str = "gemini-2.5-flash"):
    """Extract data from uploaded PDF file using Gemini AI with API key rotation"""
    logger.info(f"Starting OCR processing for file: {file.filename} with model: {model}")
    
    # Read file content
    content = await file.read()
    
    # Process using the OCR service
    result = await ocr_service.process_ocr(content, file.filename or "unknown.pdf", model)
    
    logger.info(f"OCR processing completed. Success: {result.success}")
    return result 