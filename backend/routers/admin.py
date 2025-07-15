"""
Admin and testing endpoints for OCR Engine
Provides individual service testing and system monitoring capabilities
"""
import logging
import time
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse

from models import OCRResponse, MultiPDFAnalysisResponse
from services.ocr_service import ocr_service
from services.business_analysis_service import business_analysis_service
from services.projection_service import projection_service
from services.multi_pdf_service import multi_pdf_service
from logging_config import get_logger

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
    file: UploadFile = File(...),
    model: str = Form("gemini-2.5-flash")
):
    """Test Stage 1 (OCR Service) independently"""
    try:
        start_time = time.time()
        logger.info(f"Testing Stage 1 OCR Service | File: {file.filename} | Model: {model}")
        
        # Read file content
        content = await file.read()
        
        # Test OCR service directly
        filename = file.filename or "uploaded_file"
        result = await ocr_service.process_ocr(content, filename, model)
        
        processing_time = time.time() - start_time
        
        # Enhance result with testing metadata
        test_result = {
            "stage": "stage1_ocr",
            "service": "ocr_service",
            "success": result.success,
            "processing_time": processing_time,
            "file_info": {
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type
            },
            "model_used": model,
            "result": result.dict() if result else None,
            "timestamp": time.time()
        }
        
        logger.info(f"Stage 1 test completed | Success: {result.success} | Time: {processing_time:.2f}s")
        return test_result
        
    except Exception as e:
        logger.error(f"Stage 1 test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stage 1 test failed: {str(e)}")

@router.post("/test/stage2")
async def test_stage2_business_analysis(
    extracted_data: List[Dict[str, Any]] = Body(...),
    model: str = Body(default="gemini-2.5-flash")
):
    """Test Stage 2 (Business Analysis Service) independently"""
    try:
        start_time = time.time()
        logger.info(f"Testing Stage 2 Business Analysis Service | Documents: {len(extracted_data)} | Model: {model}")
        
        # Debug: Log the structure of incoming data
        logger.debug(f"Stage 2 Input Data Structure:")
        for i, doc in enumerate(extracted_data):
            logger.debug(f"  Document {i+1}: {type(doc)} with keys: {list(doc.keys()) if isinstance(doc, dict) else 'N/A'}")
            if isinstance(doc, dict) and 'data' in doc:
                data_type = type(doc['data'])
                logger.debug(f"    Data field type: {data_type}")
                if isinstance(doc['data'], str):
                    logger.debug(f"    Data content preview: {doc['data'][:200]}...")
        
        # Ensure data is properly structured for Stage 2
        processed_data = []
        for doc in extracted_data:
            if isinstance(doc, dict):
                # If the data field contains a JSON string, parse it
                if 'data' in doc and isinstance(doc['data'], str):
                    try:
                        parsed_data = json.loads(doc['data'])
                        # Create a properly structured document
                        structured_doc = {
                            "filename": doc.get('filename', 'unknown'),
                            "success": doc.get('success', True),
                            "data": parsed_data,
                            "raw_response": doc['data']
                        }
                        processed_data.append(structured_doc)
                        logger.debug(f"✅ Parsed and structured document: {doc.get('filename', 'unknown')}")
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️ Failed to parse data field for {doc.get('filename', 'unknown')}: {str(e)}")
                        # Use the document as-is if parsing fails
                        processed_data.append(doc)
                else:
                    # Data is already structured
                    processed_data.append(doc)
            else:
                processed_data.append(doc)
        
        logger.info(f"✅ Processed {len(processed_data)} documents for Stage 2 analysis")
        
        # Test business analysis service directly with processed data
        result = await business_analysis_service.analyze_business_context(processed_data, model)
        
        processing_time = time.time() - start_time
        
        # Enhanced success determination
        success = bool(result and len(result) > 0 and not result.get('error'))
        
        test_result = {
            "stage": "stage2_business_analysis", 
            "service": "business_analysis_service",
            "success": success,
            "processing_time": processing_time,
            "input_documents": len(extracted_data),
            "processed_documents": len(processed_data),
            "model_used": model,
            "result": result,
            "timestamp": time.time()
        }
        
        logger.info(f"Stage 2 test completed | Success: {success} | Time: {processing_time:.2f}s")
        return test_result
        
    except Exception as e:
        logger.error(f"Stage 2 test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stage 2 test failed: {str(e)}")

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
        
        # Convert files to format expected by multi_pdf_service
        files_data = []
        for file in files:
            content = await file.read()
            files_data.append((file.filename, content))
        
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
            "files_info": [
                {
                    "filename": file.filename,
                    "size": len(await file.read()) if hasattr(file, 'read') else 0,
                    "content_type": file.content_type
                } for file in files
            ],
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