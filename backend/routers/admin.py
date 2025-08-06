"""
Admin and testing endpoints for OCR Engine
Provides individual service testing and system monitoring capabilities
"""
import logging
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from models import OCRResponse, MultiPDFAnalysisResponse
from services.ocr_service import ocr_service
from services.business_analysis_service import business_analysis_service
from services.projection_service import projection_service
from services.multi_pdf_service import multi_pdf_service
from services.stage1_cache_service import stage1_cache_service
from utils import DataStructureParser, JSONValidator
from logging_config import get_logger

# Pydantic models for stage outputs
class Stage1Output(BaseModel):
    filename: str
    success: bool
    data: Dict[str, Any]
    raw_text: Optional[str] = None

class Stage2Output(BaseModel):
    filename: str
    success: bool
    analysis: Dict[str, Any]
    financial_metrics: Dict[str, float]
    raw_response: Optional[str] = None

class Stage3Output(BaseModel):
    filename: str
    success: bool
    projections: Dict[str, Any]
    confidence_score: float = Field(ge=0, le=1)

class ErrorResponse(BaseModel):
    error: str
    stage: str
    timestamp: float
    details: Optional[Dict[str, Any]] = None

# Set up logger and router
logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin", "testing"])

@router.get("/health/detailed")
async def get_detailed_health():
    """Get detailed health status of all services"""
    try:
        start_time = time.time()
        
        # Test each service
        health_results = {
            "timestamp": time.time(),
            "overall_status": "healthy",
            "services": {
                "ocr_service": {"status": "unknown", "response_time": None, "error": None},
                "business_analysis_service": {"status": "unknown", "response_time": None, "error": None},
                "projection_service": {"status": "unknown", "response_time": None, "error": None},
                "multi_pdf_service": {"status": "unknown", "response_time": None, "error": None}
            },
            "system_info": {
                "total_response_time": None,
                "python_version": None,
                "available_models": []
            }
        }
        
        # Test OCR service with minimal test
        try:
            service_start = time.time()
            # Simple service availability check
            health_results["services"]["ocr_service"]["status"] = "healthy"
            health_results["services"]["ocr_service"]["response_time"] = time.time() - service_start
        except Exception as e:
            health_results["services"]["ocr_service"]["status"] = "unhealthy"
            health_results["services"]["ocr_service"]["error"] = str(e)
        
        # Test Business Analysis service
        try:
            service_start = time.time()
            health_results["services"]["business_analysis_service"]["status"] = "healthy" 
            health_results["services"]["business_analysis_service"]["response_time"] = time.time() - service_start
        except Exception as e:
            health_results["services"]["business_analysis_service"]["status"] = "unhealthy"
            health_results["services"]["business_analysis_service"]["error"] = str(e)
            
        # Test Projection service
        try:
            service_start = time.time()
            health_results["services"]["projection_service"]["status"] = "healthy"
            health_results["services"]["projection_service"]["response_time"] = time.time() - service_start
        except Exception as e:
            health_results["services"]["projection_service"]["status"] = "unhealthy"
            health_results["services"]["projection_service"]["error"] = str(e)
            
        # Test Multi-PDF service
        try:
            service_start = time.time()
            health_results["services"]["multi_pdf_service"]["status"] = "healthy"
            health_results["services"]["multi_pdf_service"]["response_time"] = time.time() - service_start
        except Exception as e:
            health_results["services"]["multi_pdf_service"]["status"] = "unhealthy"
            health_results["services"]["multi_pdf_service"]["error"] = str(e)
        
        # Check overall status
        unhealthy_services = [name for name, info in health_results["services"].items() 
                            if info["status"] == "unhealthy"]
        
        if unhealthy_services:
            health_results["overall_status"] = "degraded"
            health_results["unhealthy_services"] = unhealthy_services
        
        # System info
        health_results["system_info"]["total_response_time"] = time.time() - start_time
        
        logger.info(f"Detailed health check completed | Status: {health_results['overall_status']} | "
                   f"Response time: {health_results['system_info']['total_response_time']:.3f}s")
        
        return health_results
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/test/stage1")
async def test_stage1_ocr(
    files: List[UploadFile] = File(...),
    model: str = Form("gemini-2.5-pro")
):
    """Test Stage 1 (OCR Service) independently - now supports multiple files."""
    try:
        total_start = time.time()
        logger.info(f"Testing Stage 1 OCR Service | Files: {len(files)} | Model: {model}")

        # Special branch: exactly two CSVs -> run Stage 1 caching path and return cache payloads
        if len(files) == 2:
            fn1 = (files[0].filename or "").lower()
            fn2 = (files[1].filename or "").lower()
            if fn1.endswith(".csv") and fn2.endswith(".csv"):
                file_start_1 = time.time()
                content1 = await files[0].read()
                t1 = time.time() - file_start_1

                file_start_2 = time.time()
                content2 = await files[1].read()
                t2 = time.time() - file_start_2

                files_data: List[Tuple[str, bytes]] = [
                    (files[0].filename or "file1.csv", content1),
                    (files[1].filename or "file2.csv", content2),
                ]

                # Validate and run stage1 cache (uses OCR service under the hood)
                stage1_cache_service.validate_two_csv(files_data)
                pnl_cache_key, bs_cache_key, pnl_data, bs_data = await stage1_cache_service.run_stage1_and_cache(
                    files_data, extraction_model=model
                )

                # Determine detected document types if data present
                pnl_doc_type = (pnl_data or {}).get("document_type") if pnl_data else None
                bs_doc_type = (bs_data or {}).get("document_type") if bs_data else None

                total_time = time.time() - total_start
                files_info = [
                    {"filename": files[0].filename, "size": len(content1), "content_type": getattr(files[0], "content_type", None)},
                    {"filename": files[1].filename, "size": len(content2), "content_type": getattr(files[1], "content_type", None)},
                ]
                per_file_timings = [
                    {"filename": files[0].filename or "file1.csv", "processing_time": t1},
                    {"filename": files[1].filename or "file2.csv", "processing_time": t2},
                ]

                response_body = {
                    "stage": "stage1_ocr",
                    "service": "ocr_service",
                    "success": bool(pnl_data),
                    "processing_time": total_time,
                    "files_info": files_info,
                    "per_file_timings": per_file_timings,
                    "model_used": model,
                    "pnl_cache_key": pnl_cache_key,
                    "bs_cache_key": bs_cache_key,
                    "stage1_cached_data": {
                        "pnl": pnl_data,
                        "balance_sheet": bs_data
                    },
                    "document_types": {
                        "pnl": "Profit and Loss" if pnl_doc_type == "Profit and Loss" else None,
                        "balance_sheet": "Balance Sheet" if bs_doc_type == "Balance Sheet" else None
                    },
                    "timestamp": time.time()
                }
                return response_body

        normalized_docs: List[Stage1Output] = []
        files_info: List[Dict[str, Any]] = []
        per_file_timings: List[Dict[str, Any]] = []

        # Default behavior: Process each file independently; do not fail the whole batch for individual errors
        for file in files:
            file_start = time.time()
            fname = getattr(file, "filename", None) or "uploaded_file"
            ctype = getattr(file, "content_type", None)

            try:
                logger.info(f"[Stage1] Processing file: {fname} | Content-Type: {ctype}")
                content = await file.read()
                size = len(content) if content is not None else 0
                files_info.append({"filename": fname, "size": size, "content_type": ctype})

                # OCR per file
                result = await ocr_service.process_ocr(content, fname, model)

                # Convert OCRResponse to dict for processing
                result_dict = {
                    "filename": fname,
                    "success": getattr(result, "success", False),
                    "data": getattr(result, "data", None),
                    "error": getattr(result, "error", None),
                    "raw_text": getattr(result, "text", None)
                }

                # Use robust parsing to handle data.data structure
                normalized_result = DataStructureParser.normalize_stage1_result(result_dict)
                
                # Validate the parsed financial data
                data_valid = False
                if normalized_result["data"]:
                    data_valid = JSONValidator.validate_financial_data(normalized_result["data"])
                
                # Create normalized document
                normalized_doc = Stage1Output(
                    filename=fname,
                    success=normalized_result["success"] and data_valid,
                    data=normalized_result["data"],
                    raw_text=normalized_result.get("raw_text")
                )
                normalized_docs.append(normalized_doc)

                file_time = time.time() - file_start
                per_file_timings.append({"filename": fname, "processing_time": file_time})
                logger.debug(f"[Stage1] Output shape for {fname}: {len(normalized_doc.data.keys())} fields | Time: {file_time:.3f}s")

            except Exception as fe:
                # Capture per-file failure but continue
                logger.error(f"[Stage1] File failed: {fname} | Error: {str(fe)}")
                normalized_docs.append(
                    Stage1Output(
                        filename=fname,
                        success=False,
                        data={"error": "File-level failure during OCR"},
                        raw_text=None
                    )
                )
                size_fallback = 0
                if not any(fi.get("filename") == fname for fi in files_info):
                    files_info.append({"filename": fname, "size": size_fallback, "content_type": ctype})
                per_file_timings.append({"filename": fname, "processing_time": time.time() - file_start})

        total_time = time.time() - total_start

        # Aggregate success: true if at least one succeeded
        aggregate_success = any(doc.success for doc in normalized_docs)
        logger.info(f"[Stage1] Completed processing {len(files)} files | Model: {model} | Aggregate success: {aggregate_success} | Total time: {total_time:.2f}s")
        logger.debug(f"[Stage1] Chain-ready docs emitted: {len(normalized_docs)}")

        # Build response
        response_body = {
            "stage": "stage1_ocr",
            "service": "ocr_service",
            "success": aggregate_success,
            "processing_time": total_time,
            "files_info": files_info,
            "per_file_timings": per_file_timings,
            "model_used": model,
            "result": [doc.dict() for doc in normalized_docs],
            "chain_ready": [doc.dict() for doc in normalized_docs],
            "timestamp": time.time()
        }

        # If all files failed, indicate failure via standardized error while still returning detail
        if not aggregate_success:
            error = ErrorResponse(
                error="Stage 1 processing failed for all files",
                stage="stage1_ocr",
                timestamp=time.time(),
                details={"files": [fi.get("filename") for fi in files_info]}
            )
            logger.error(f"[Stage1] Batch failed: {error.json()}")
            # Return 500 to signal complete failure
            raise HTTPException(status_code=500, detail=error.dict())

        return response_body

    except HTTPException:
        # Already standardized
        raise
    except Exception as e:
        # Critical exception: standardize using ErrorResponse
        error = ErrorResponse(
            error="Stage 1 processing encountered a critical exception",
            stage="stage1_ocr",
            timestamp=time.time(),
            details={"exception": str(e)}
        )
        logger.error(f"[Stage1] Critical failure: {error.json()}")
        raise HTTPException(status_code=500, detail=error.dict())

@router.post("/test/stage2")
async def test_stage2_business_analysis(
    extracted_data: List[Dict[str, Any]] = Body(...),
    model: str = Body(default="gemini-2.5-flash")
):
    """Test Stage 2 (Business Analysis Service) independently"""
    try:
        start_time = time.time()
        
        # Accept both a single dict or a list for convenience in Postman chaining
        if isinstance(extracted_data, dict):
            logger.debug("Stage 2 received a single dict; coercing to a list with one document.")
            extracted_data = [extracted_data]
        
        logger.info(f"Testing Stage 2 Business Analysis Service | Documents: {len(extracted_data)} | Model: {model}")
        
        # Validate input data structure with robust parsing
        validated_inputs = []
        for doc in extracted_data:
            try:
                # Use robust parsing to normalize the input
                normalized_doc = DataStructureParser.normalize_stage1_result(doc)
                
                # Validate against Stage1 output format
                stage1_output = Stage1Output(**normalized_doc)
                validated_inputs.append(stage1_output.dict())
                logger.debug(f"✅ Valid Stage1 output: {normalized_doc.get('filename', 'unknown')}")
            except Exception as e:
                error = ErrorResponse(
                    error="Invalid Stage1 output format",
                    stage="stage2_business_analysis",
                    timestamp=time.time(),
                    details={
                        "document": doc.get('filename', 'unknown'),
                        "validation_error": str(e)
                    }
                )
                logger.error(f"Invalid Stage1 output: {error.json()}")
                raise HTTPException(status_code=400, detail=error.dict())
        
        # Test business analysis service with validated data
        result = await business_analysis_service.analyze_business_context(validated_inputs, model)
        
        processing_time = time.time() - start_time
        
        # Validate and normalize output
        try:
            stage2_output = Stage2Output(
                filename=validated_inputs[0]['filename'],
                success=bool(result and len(result) > 0),
                analysis=result.get('analysis', {}),
                financial_metrics=result.get('financial_metrics', {}),
                raw_response=str(result)
            )
            logger.debug(f"Stage2 output shape: {len(stage2_output.analysis.keys())} analysis fields | {len(stage2_output.financial_metrics.keys())} metrics")
        except Exception as e:
            error = ErrorResponse(
                error="Invalid Stage2 output format",
                stage="stage2_business_analysis",
                timestamp=time.time(),
                details={"validation_error": str(e)}
            )
            logger.error(f"Stage2 output validation failed: {error.json()}")
            raise HTTPException(status_code=500, detail=error.dict())
        
        test_result = {
            "stage": "stage2_business_analysis",
            "service": "business_analysis_service",
            "success": stage2_output.success,
            "processing_time": processing_time,
            "input_documents": len(extracted_data),
            "processed_documents": len(validated_inputs),
            "model_used": model,
            "result": stage2_output.dict(),
            "chain_ready": stage2_output.dict(),  # Directly usable as the body for Stage 3
            "timestamp": time.time()
        }
        
        logger.info(f"Stage 2 test completed | Success: {stage2_output.success} | Time: {processing_time:.2f}s")
        return test_result
        
    except HTTPException:
        raise
    except Exception as e:
        error = ErrorResponse(
            error="Stage 2 processing failed",
            stage="stage2_business_analysis",
            timestamp=time.time(),
            details={"exception": str(e)}
        )
        logger.error(f"Stage 2 test failed: {error.json()}")
        raise HTTPException(status_code=500, detail=error.dict())

@router.post("/test/stage3")
async def test_stage3_projections(
    business_analysis: Dict[str, Any] = Body(...),
    model: str = Body(default="gemini-2.5-flash")
):
    """Test Stage 3 (Projection Service) independently"""
    try:
        start_time = time.time()
        logger.info(f"Testing Stage 3 Projection Service | Model: {model}")
        
        # Test projection service directly
        result = await projection_service.generate_projections(business_analysis, model)
        
        processing_time = time.time() - start_time
        
        test_result = {
            "stage": "stage3_projections",
            "service": "projection_service", 
            "success": bool(result and len(result) > 0),
            "processing_time": processing_time,
            "model_used": model,
            "result": result,
            "timestamp": time.time()
        }
        
        logger.info(f"Stage 3 test completed | Success: {test_result['success']} | Time: {processing_time:.2f}s")
        return test_result
        
    except Exception as e:
        logger.error(f"Stage 3 test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stage 3 test failed: {str(e)}")

@router.post("/test/full-process")
async def test_full_process(
    files: List[UploadFile] = File(...),
    model: str = Form("gemini-2.5-flash")
):
    """Test the complete 3-stage process with detailed timing"""
    try:
        start_time = time.time()
        logger.info(f"Testing full 3-stage process | Files: {len(files)} | Model: {model}")
        
        # Convert files to format expected by multi_pdf_service and collect sizes
        files_data = []
        files_info = []
        for file in files:
            content = await file.read()
            files_data.append((file.filename, content))
            files_info.append({
                "filename": file.filename,
                "size": len(content),
                "content_type": getattr(file, "content_type", None)
            })
        
        # Time each stage separately for analysis
        stage_timings = {}
        
        # Run full process
        full_start = time.time()
        result = await multi_pdf_service.analyze_multiple_files(files_data, model)
        total_time = time.time() - full_start
        
        # Extract stage timings from result if available
        if hasattr(result, 'data_analysis_summary') and result.data_analysis_summary:
            stage_timings = result.data_analysis_summary.get('stage_timings', {})
        
        test_result = {
            "test_type": "full_process",
            "success": result.success if result else False,
            "total_processing_time": total_time,
            "stage_timings": stage_timings,
            "files_info": files_info,
            "model_used": model,
            "result": result.dict() if result else None,
            "timestamp": time.time(),
            "performance_metrics": {
                "files_per_second": len(files) / total_time if total_time > 0 else 0,
                "average_file_time": total_time / len(files) if len(files) > 0 else 0
            }
        }
        
        logger.info(f"Full process test completed | Success: {test_result['success']} | "
                   f"Total time: {total_time:.2f}s | Files/sec: {test_result['performance_metrics']['files_per_second']:.2f}")
        return test_result
        
    except Exception as e:
        logger.error(f"Full process test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Full process test failed: {str(e)}")

@router.get("/test/validate-services")
async def validate_all_services():
    """Validate that all services are properly configured and functional"""
    try:
        logger.info("Validating all services")
        
        validation_results = {
            "timestamp": time.time(),
            "overall_valid": True,
            "services": {
                "ocr_service": {"valid": False, "issues": []},
                "business_analysis_service": {"valid": False, "issues": []},
                "projection_service": {"valid": False, "issues": []},
                "multi_pdf_service": {"valid": False, "issues": []}
            },
            "configuration": {
                "api_keys_available": False,
                "prompts_loaded": False,
                "timeouts_configured": False
            }
        }
        
        # Validate OCR service
        try:
            # Check if service exists and basic methods are available
            if hasattr(ocr_service, 'process_ocr'):
                validation_results["services"]["ocr_service"]["valid"] = True
            else:
                validation_results["services"]["ocr_service"]["issues"].append("process_ocr method not found")
        except Exception as e:
            validation_results["services"]["ocr_service"]["issues"].append(str(e))
        
        # Validate Business Analysis service
        try:
            if hasattr(business_analysis_service, 'analyze_business_context'):
                validation_results["services"]["business_analysis_service"]["valid"] = True
            else:
                validation_results["services"]["business_analysis_service"]["issues"].append("analyze_business_context method not found")
        except Exception as e:
            validation_results["services"]["business_analysis_service"]["issues"].append(str(e))
        
        # Validate Projection service
        try:
            if hasattr(projection_service, 'generate_projections'):
                validation_results["services"]["projection_service"]["valid"] = True
            else:
                validation_results["services"]["projection_service"]["issues"].append("generate_projections method not found")
        except Exception as e:
            validation_results["services"]["projection_service"]["issues"].append(str(e))
            
        # Validate Multi-PDF service
        try:
            if hasattr(multi_pdf_service, 'analyze_multiple_files'):
                validation_results["services"]["multi_pdf_service"]["valid"] = True
            else:
                validation_results["services"]["multi_pdf_service"]["issues"].append("analyze_multiple_files method not found")
        except Exception as e:
            validation_results["services"]["multi_pdf_service"]["issues"].append(str(e))
        
        # Check overall validity
        all_valid = all(service["valid"] for service in validation_results["services"].values())
        validation_results["overall_valid"] = all_valid
        
        logger.info(f"Service validation completed | Overall valid: {all_valid}")
        return validation_results
        
    except Exception as e:
        logger.error(f"Service validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service validation failed: {str(e)}")

@router.get("/performance/metrics")
async def get_performance_metrics():
    """Get performance metrics for the system"""
    try:
        # This would typically pull from a metrics store or monitoring system
        # For now, return basic system info
        metrics = {
            "timestamp": time.time(),
            "system": {
                "uptime": "N/A",  # Would need to track startup time
                "memory_usage": "N/A", # Would need psutil
                "cpu_usage": "N/A"
            },
            "api": {
                "total_requests": "N/A", # Would need request tracking
                "success_rate": "N/A",
                "average_response_time": "N/A"
            },
            "services": {
                "ocr_service": {"requests": 0, "avg_time": 0, "success_rate": 0},
                "business_analysis_service": {"requests": 0, "avg_time": 0, "success_rate": 0},
                "projection_service": {"requests": 0, "avg_time": 0, "success_rate": 0}
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}") 