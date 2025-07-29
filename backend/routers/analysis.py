"""
Multi-document analysis endpoints
ENHANCED: Updated projection counting and logging
"""
import time
from typing import List
from fastapi import APIRouter, File, UploadFile, Form
from models import MultiPDFAnalysisResponse
from services.orchestration_service import orchestration_service
from logging_config import get_logger, log_request_start, log_request_end, log_file_processing

logger = get_logger(__name__)
router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/analyze", response_model=MultiPDFAnalysisResponse)
async def analyze_multiple_files(files: List[UploadFile] = File(...), model: str = Form(default="gemini-2.5-pro"), projection_start_date: str = Form(default="2026-01-01")):
    """Analyze multiple files with optimized logging"""
    request_start_time = time.time()
    total_size_mb = sum(getattr(file, 'size', 0) for file in files) / (1024 * 1024)
    # Single request start log instead of multiple file logs
    logger.info(f" Request started | Files: {len(files)} | Size: {total_size_mb:.2f}MB")
    try:
        # Remove individual file reading logs, just log completion
        files_data = []
        for file in files:
            content = await file.read()
            files_data.append((file.filename or "unknown", content))
        logger.debug(f" Files read | Duration: {time.time() - request_start_time:.1f}s")
        # Process files
        result = await orchestration_service.analyze_multiple_files(files_data, model, projection_start_date)
        # Single completion log
        total_time = time.time() - request_start_time
        logger.info(f"✅ Request complete | Duration: {total_time:.1f}s | Success: {result.success}")
        return result
    except Exception as e:
        total_time = time.time() - request_start_time
        logger.error(f"❌ Request failed | Duration: {total_time:.1f}s | Error: {str(e)}")
        raise