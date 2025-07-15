"""
OCR processing endpoints
"""
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from models import OCRResponse
from services.ocr_service import ocr_service
from logging_config import get_logger, log_request_start, log_request_end

logger = get_logger(__name__)
router = APIRouter(tags=["ocr"])

@router.post("/ocr", response_model=OCRResponse)
async def process_ocr(
    file: UploadFile = File(...), 
    model: str = Form(default="gemini-2.5-pro")
):
    """Extract data from uploaded image, PDF, or CSV file using Gemini AI with API key rotation"""
    # Validate that we have a file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Log request start
    file_extension = Path(file.filename).suffix.lower()
    log_request_start(logger, "OCR processing", 
                     filename=file.filename, extension=file_extension, 
                     content_type=file.content_type, model=model)
    
    try:
        # Read file content
        content = await file.read()
        logger.debug(f"File content read | Size: {len(content)} bytes")
        
        # Process using the OCR service
        result = await ocr_service.process_ocr(content, file.filename, model)
        
        log_request_end(logger, "OCR processing", success=result.success, duration=0,
                       filename=file.filename)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"OCR processing unexpected error | File: {file.filename} | Error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error during file processing: {str(e)}"
        ) 