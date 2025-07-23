"""
Multi-document analysis endpoints
ENHANCED: Updated projection counting and logging
"""
import time
from typing import List
from fastapi import APIRouter, File, UploadFile, Form
from models import MultiPDFAnalysisResponse
from services.multi_pdf_service import multi_pdf_service
from logging_config import get_logger, log_request_start, log_request_end, log_file_processing

logger = get_logger(__name__)
router = APIRouter(prefix="/multi-pdf", tags=["multi-pdf"])

@router.post("/analyze", response_model=MultiPDFAnalysisResponse)
async def analyze_multiple_files(
    files: List[UploadFile] = File(...), 
    model: str = Form(default="gemini-2.5-pro")
):
    """
    Analyze multiple PDF and CSV files with data extraction, normalization, and projections
    
    - **files**: List of PDF and/or CSV files to analyze (max 10 files, 50MB each for PDFs, 25MB each for CSVs)
    - **model**: Gemini model to use for analysis (default: gemini-2.5-pro)
    
    Supported file types:
    - PDF documents (financial statements, reports, etc.)
    - CSV files (financial data in tabular format)
    
    Returns comprehensive analysis with:
    - Extracted data from each document
    - Normalized and combined data
    - Complete financial projections (Revenue, Expenses, Gross Profit, Net Profit)
    - Projections for 1, 3, 5, 10, and 15 year horizons
    - Detailed explanations and business intelligence
    """
    request_start_time = time.time()
    
    # Log request details
    total_size_mb = sum(getattr(file, 'size', 0) for file in files) / (1024 * 1024)
    log_request_start(logger, "multi-pdf analyze", 
                     files=len(files), model=model, total_size_mb=f"{total_size_mb:.2f}")
    
    # Log individual file details
    for i, file in enumerate(files, 1):
        file_size = getattr(file, 'size', 0) if hasattr(file, 'size') else 0
        log_file_processing(logger, "received", file.filename or f"file_{i}", 
                          file_size=file_size)
    
    try:
        logger.info(f"Reading {len(files)} files into memory")
        
        # Read all file contents
        files_data = []
        for i, file in enumerate(files, 1):
            logger.debug(f"Reading file {i}/{len(files)} | Name: {file.filename}")
            content = await file.read()
            files_data.append((file.filename or "unknown", content))
            log_file_processing(logger, "read", file.filename or f"file_{i}", 
                              file_size=len(content), success=True)
        
        file_read_time = time.time() - request_start_time
        logger.info(f"File reading completed | Duration: {file_read_time:.2f}s | Starting analysis")
        
        # Process using the multi-file service
        result = await multi_pdf_service.analyze_multiple_files(files_data, model)
        
        total_request_time = time.time() - request_start_time
        
        # Enhanced projection counting and logging
        files_processed = len(result.extracted_data) if result.extracted_data else 0
        
        # Count projections more accurately
        projections_count = 0
        if result.projections:
            # Check for base_case_projections (new structure)
            base_case = result.projections.get('base_case_projections', {})
            if base_case:
                # Count metrics across all horizons
                required_metrics = ['revenue', 'expenses', 'gross_profit', 'net_profit']
                required_horizons = ['1_year_ahead', '3_years_ahead', '5_years_ahead', '10_years_ahead', '15_years_ahead']
                
                for horizon in required_horizons:
                    if horizon in base_case:
                        horizon_data = base_case[horizon]
                        if isinstance(horizon_data, dict):
                            for metric in required_metrics:
                                if metric in horizon_data:
                                    metric_data = horizon_data[metric]
                                    if isinstance(metric_data, list) and len(metric_data) > 0:
                                        projections_count += 1
                
                logger.info(f"🎯 PROJECTION COUNT: {projections_count} metrics found across {len(base_case)} horizons")
            else:
                # Fallback to specific_projections (legacy structure)
                projections_count = len(result.projections.get('specific_projections', {}))
                logger.info(f"🎯 LEGACY PROJECTION COUNT: {projections_count} projections found")
        
        # Enhanced logging with projection metrics
        log_request_end(logger, "multi-pdf analyze", success=result.success, duration=total_request_time,
                       files_processed=f"{files_processed}/{len(files)}",
                       data_quality_score=result.data_quality_score,
                       projections_generated=projections_count)
        
        # Log detailed projection summary
        if result.success and projections_count > 0:
            expected_metrics = 20  # 4 metrics × 5 horizons
            completeness_rate = (projections_count / expected_metrics * 100) if projections_count > 0 else 0
            complete_horizons = projections_count // 4
            
            logger.info(f"🎯 PROJECTION SUMMARY:")
            logger.info(f"   📊 Total metrics generated: {projections_count}/{expected_metrics}")
            logger.info(f"   📈 Completeness rate: {completeness_rate:.1f}%")
            logger.info(f"   🕐 Complete horizons: {complete_horizons}/5")
            logger.info(f"   📋 Metrics per horizon: Revenue, Expenses, Gross Profit, Net Profit")
            
            if projections_count == expected_metrics:
                logger.info("✅ ALL REQUIRED PROJECTION DATA GENERATED SUCCESSFULLY")
            elif projections_count >= 16:  # At least 4 complete horizons
                logger.info("✅ SUBSTANTIAL PROJECTION DATA GENERATED")
            elif projections_count > 0:
                logger.warning("⚠️ PARTIAL PROJECTION DATA GENERATED - Some metrics may be missing")
            else:
                logger.error("❌ NO PROJECTION DATA GENERATED")
        
        if not result.success:
            logger.error(f"Analysis failed | Error: {result.error}")
        
        return result
        
    except Exception as e:
        total_request_time = time.time() - request_start_time
        log_request_end(logger, "multi-pdf analyze", success=False, duration=total_request_time,
                       error=str(e))
        raise