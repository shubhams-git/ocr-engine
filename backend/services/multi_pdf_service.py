"""
Enhanced Multi-PDF analysis service using separate stage-based services
Orchestrates OCR Service, Business Analysis Service, and Projection Service

Key Features:
- Modular 3-stage architecture using separate services
- Tiered model selection: Flash for extraction, Pro for analysis
- Semaphore-controlled concurrency for Pro model calls
- Enhanced business context analysis and pattern recognition
- Advanced projection engine with multiple forecasting methods
- Comprehensive validation and reconciliation
- Australian FY-focused projections with industry intelligence
"""
import logging
import asyncio
import tempfile
import os
import json
import re
import time
import base64
from typing import List, Tuple, Dict, Any, Optional, Union, cast
from fastapi import HTTPException

from config import API_KEYS, OVERALL_PROCESS_TIMEOUT
from models import MultiPDFAnalysisResponse, OCRResponse
from logging_config import (get_logger, log_request_start, log_request_end, 
                          log_stage_progress, log_validation_result)

# Import the separate services
from services.ocr_service import ocr_service
from services.business_analysis_service import business_analysis_service
from services.projection_service import projection_service

# Set up logger
logger = get_logger(__name__)

class EnhancedMultiPDFService:
    """Enhanced service for orchestrating multi-document financial analysis using separate stage services"""
    
    def __init__(self):
        self.max_pdf_size = 50 * 1024 * 1024   # 50MB for PDFs
        self.max_csv_size = 25 * 1024 * 1024   # 25MB for CSV files
        self.max_files = 10
        
        # Timeout configuration
        self.overall_process_timeout = OVERALL_PROCESS_TIMEOUT
        
        # TIERED MODEL SELECTION & CONCURRENCY CONTROL
        # Stage 1: Use Flash for data extraction (higher quotas, simpler task)
        self.stage1_model = "gemini-2.5-flash"
        
        # Stages 2-3: Use Pro for complex analysis (lower quotas, complex reasoning)
        # Semaphore to limit concurrent Pro model calls to prevent quota exhaustion
        self.pro_model_semaphore = asyncio.Semaphore(3)  # Max 3 concurrent Pro calls
        
        # Only log during main server process, not during uvicorn reloads
        if os.getenv("OCR_SERVER_MAIN") == "true":
            logger.info("Enhanced Multi-PDF Service initialized | Architecture: 3-Stage Modular Services")
            logger.info("🎯 TIERED MODEL SELECTION | Stage 1: Flash (extraction) | Stages 2-3: Pro (analysis)")
            logger.info(f"⚡ CONCURRENCY CONTROL | Pro model semaphore limit: {self.pro_model_semaphore._value}")
        
        logger.debug(f"Service configuration | Max files: {self.max_files} | PDF limit: {self.max_pdf_size//1024//1024}MB | CSV limit: {self.max_csv_size//1024//1024}MB")
        logger.debug(f"Overall process timeout: {self.overall_process_timeout}s")
        logger.debug("Using separate services: OCR Service (Stage 1), Business Analysis Service (Stage 2), Projection Service (Stage 3)")
        logger.debug(f"Model strategy: Stage 1 extraction uses {self.stage1_model}, Stages 2-3 analysis uses gemini-2.5-pro")
    
    def get_analysis_model(self, requested_model: str) -> str:
        """
        Determine the appropriate Pro model for analysis stages (2-3)
        Always returns a Pro model regardless of what was requested
        """
        if "pro" in requested_model.lower():
            return requested_model
        else:
            # Default to Pro for complex analysis even if Flash was requested
            return "gemini-2.5-pro"
    
    def get_file_type_and_mime(self, filename: str, content: bytes) -> Tuple[str, str]:
        """Determine file type and MIME type"""
        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.csv'):
            logger.debug(f"📄 File type detected: CSV - {filename}")
            return 'csv', 'text/csv'
        elif filename_lower.endswith('.pdf'):
            if not content.startswith(b'%PDF'):
                raise HTTPException(status_code=400, detail=f"Invalid PDF: {filename}")
            logger.debug(f"📑 File type detected: PDF - {filename}")
            return 'pdf', 'application/pdf'
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {filename}. Use PDF or CSV only."
        )
    
    def validate_files(self, files_data: List[Tuple[str, bytes]]) -> None:
        """Validate uploaded files"""
        if not files_data:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files_data) > self.max_files:
            raise HTTPException(status_code=400, detail=f"Maximum {self.max_files} files allowed")
        
        logger.info(f"🔍 Validating {len(files_data)} files...")
        
        for filename, content in files_data:
            if not filename or len(content) == 0:
                raise HTTPException(status_code=400, detail=f"Invalid file: {filename}")
            
            file_type, _ = self.get_file_type_and_mime(filename, content)
            file_size_mb = len(content) / 1024 / 1024
            
            if file_type == 'pdf' and len(content) > self.max_pdf_size:
                raise HTTPException(status_code=413, detail=f"PDF {filename} too large (max 50MB)")
            elif file_type == 'csv' and len(content) > self.max_csv_size:
                raise HTTPException(status_code=413, detail=f"CSV {filename} too large (max 25MB)")
            
            logger.info(f"✅ File validated: {filename} ({file_type.upper()}, {file_size_mb:.2f}MB)")
        
        logger.info("✅ All files validated successfully")
    
    async def _internal_analyze_multiple_files(self, files_data: List[Tuple[str, bytes]], requested_model: str = "gemini-2.5-pro") -> MultiPDFAnalysisResponse:
        """
        Internal method for 3-stage multi-file analysis using separate services with tiered model selection
        """
        overall_start_time = time.time()
        
        # Determine models for each stage
        extraction_model = self.stage1_model  # Always use Flash for extraction
        analysis_model = self.get_analysis_model(requested_model)  # Use Pro for analysis
        
        try:
            log_request_start(logger, "multi-file analysis", 
                            files=len(files_data), model=f"Stage1:{extraction_model}|Stage2-3:{analysis_model}", 
                            api_keys_available=len(API_KEYS), architecture="3-Stage Modular Services")
            
            logger.info(f"🎯 TIERED MODEL SELECTION | Stage 1: {extraction_model} | Stages 2-3: {analysis_model}")
            
            # File validation
            self.validate_files(files_data)
            
            # STAGE 1: Parallel Data Extraction, Normalization & Quality Assessment using Flash Model
            log_stage_progress(logger, "1", "STARTED", f"OCR Service parallel processing | Model: {extraction_model} | Tasks: {len(files_data)}")
            stage1_start = time.time()
            
            # Use Flash model for all Stage 1 extractions (higher quotas, simpler task)
            stage1_tasks = [
                ocr_service.process_ocr(content, filename, extraction_model)
                for filename, content in files_data
            ]
            
            stage1_results = await asyncio.gather(*stage1_tasks, return_exceptions=True)
            stage1_time = time.time() - stage1_start
            
            # Process Stage 1 results
            successful_extractions = []
            failed_extractions = []
            doc_types = {}
            
            for result in stage1_results:
                if isinstance(result, Exception):
                    failed_extractions.append(str(result))
                    logger.error(f"Stage 1 exception | Error: {str(result)}")
                    continue
                
                ocr_response = cast(OCRResponse, result)
                
                try:
                    if ocr_response.success:
                        if isinstance(ocr_response.data, str):
                            parsed_data = json.loads(ocr_response.data)
                        else:
                            parsed_data = ocr_response.data
                        
                        extraction_result = {
                            "filename": parsed_data.get('source_filename', 'Unknown'),
                            "success": True,
                            "data": parsed_data,
                            "raw_response": ocr_response.data
                        }
                        successful_extractions.append(extraction_result)
                        
                        filename = extraction_result.get('filename', 'Unknown')
                        doc_type = parsed_data.get('document_type', 'Other')
                        doc_types[filename] = doc_type
                        logger.info(f"Stage 1 SUCCESS | File: {filename} | Type: {doc_type} | Model: {extraction_model}")
                    else:
                        error_msg = ocr_response.error or 'Unknown error'
                        failed_extractions.append(error_msg)
                        logger.error(f"Stage 1 FAILED | Error: {error_msg}")
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.error(f"Stage 1 processing error | Error: {str(e)}")
                    failed_extractions.append(f"Processing error: {str(e)}")
            
            if not successful_extractions:
                logger.error(f"Stage 1 CRITICAL FAILURE | All extractions failed | Errors: {len(failed_extractions)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Data extraction failed for all files. Errors: {failed_extractions}"
                )
            
            # Check for mandatory P&L
            has_profit_loss = any(doc_type == 'Profit and Loss' for doc_type in doc_types.values())
            if not has_profit_loss:
                logger.error("P&L validation FAILED | No Profit & Loss statement detected")
                raise HTTPException(
                    status_code=400,
                    detail="No Profit & Loss statement detected. Please upload at least one P&L document for accurate financial projections."
                )
            
            log_stage_progress(logger, "1", "COMPLETED", f"Duration: {stage1_time:.2f}s | Success: {len(successful_extractions)}/{len(files_data)} | Model: {extraction_model}")
            logger.debug(f"Document types extracted | {doc_types}")
            
            # STAGE 2: Business Analysis & Methodology Selection using Pro Model with Semaphore
            log_stage_progress(logger, "2", "STARTED", f"Business Analysis Service | Model: {analysis_model} | Semaphore: {self.pro_model_semaphore._value}")
            stage2_start = time.time()
            
            # Use semaphore to control Pro model concurrency
            async with self.pro_model_semaphore:
                logger.debug(f"🔒 Acquired Pro model semaphore for Stage 2 | Available: {self.pro_model_semaphore._value}")
                stage2_result = await business_analysis_service.analyze_business_context(successful_extractions, analysis_model)
                logger.debug(f"🔓 Released Pro model semaphore from Stage 2 | Available: {self.pro_model_semaphore._value + 1}")
            
            stage2_time = time.time() - stage2_start
            
            business_stage = stage2_result.get('business_context', {}).get('business_stage', 'Unknown')
            selected_method = stage2_result.get('methodology_evaluation', {}).get('selected_method', {}).get('primary_method', 'Unknown')
            
            log_stage_progress(logger, "2", "COMPLETED", f"Duration: {stage2_time:.2f}s | Business Stage: {business_stage} | Method: {selected_method} | Model: {analysis_model}")
            
            # STAGE 3: Projection Engine using Pro Model with Semaphore
            log_stage_progress(logger, "3", "STARTED", f"Projection Service | Model: {analysis_model} | Semaphore: {self.pro_model_semaphore._value}")
            stage3_start = time.time()
            
            # Use semaphore to control Pro model concurrency
            async with self.pro_model_semaphore:
                logger.debug(f"🔒 Acquired Pro model semaphore for Stage 3 | Available: {self.pro_model_semaphore._value}")
                stage3_result = await projection_service.generate_projections(stage2_result, analysis_model)
                logger.debug(f"🔓 Released Pro model semaphore from Stage 3 | Available: {self.pro_model_semaphore._value + 1}")
            
            stage3_time = time.time() - stage3_start
            
            projections_count = len(stage3_result.get('base_case_projections', {}))
            
            log_stage_progress(logger, "3", "COMPLETED", f"Duration: {stage3_time:.2f}s | Projections: {projections_count} | Model: {analysis_model}")
            
            # LOCAL VALIDATION using Projection Service
            logger.info(f"🔍 LOCAL VALIDATION: Financial Reconciliation")
            validation_start = time.time()
            
            local_validation_results = await projection_service.validate_projections(stage3_result)
            validation_time = time.time() - validation_start
            
            logger.info(f"✅ Local Validation Complete ({validation_time:.2f}s): Score={local_validation_results.get('overall_score', 0):.2f}")
            validation_score = local_validation_results.get('overall_score', 0)
            if not local_validation_results['valid']:
                issues_count = len(local_validation_results.get('errors', []))
                logger.warning(f"Validation completed with issues | Count: {issues_count}")
            
            # Calculate totals
            total_time = time.time() - overall_start_time
            total_api_calls = len(files_data) + 2  # Stage 1 parallel + Stage 2 + Stage 3
            
            log_request_end(logger, "multi-file analysis", success=True, duration=total_time,
                          files_processed=f"{len(successful_extractions)}/{len(files_data)}",
                          api_calls=total_api_calls, validation_score=f"{validation_score:.2f}")
            
            # Assemble comprehensive response
            response = MultiPDFAnalysisResponse(
                success=True,
                extracted_data=successful_extractions,
                normalized_data=stage2_result,
                projections=stage3_result,
                explanation=stage3_result.get('executive_summary', 'Enhanced 3-stage financial analysis completed with tiered model selection'),
                error=None,
                
                # Enhanced fields from business analysis
                data_quality_score=local_validation_results.get('overall_score'),
                confidence_levels=projection_service.get_confidence_levels(stage3_result),
                assumptions=self._transform_assumptions(stage3_result.get('assumption_documentation', {}).get('critical_assumptions', [])),
                risk_factors=self._transform_risk_factors(stage2_result.get('handover_recommendations', {}).get('risk_adjustments', [])),
                methodology=projection_service.get_methodology_string(stage3_result),
                scenarios=stage3_result.get('scenario_projections', {}),
                
                # Period detection fields
                period_granularity=successful_extractions[0].get('data', {}).get('basic_context', {}).get('reporting_frequency', 'monthly') if successful_extractions else 'monthly',
                total_data_points=sum(result.get('data', {}).get('data_quality_assessment', {}).get('total_periods', 0) for result in successful_extractions),
                time_span=f"Multi-document analysis spanning {len(successful_extractions)} documents",
                seasonality_detected=stage2_result.get('contextual_analysis', {}).get('seasonality_patterns', {}).get('seasonal_detected', False),
                data_analysis_summary={
                    'document_types': doc_types,
                    'extraction_success_rate': len(successful_extractions) / len(files_data),
                    'business_context': stage2_result.get('business_context', {}),
                    'local_validation_results': local_validation_results,
                    'processing_stages_completed': 3,
                    'architecture_type': '3-stage_modular_services',
                    'tiered_model_selection': {
                        'stage1_extraction_model': extraction_model,
                        'stage2_analysis_model': analysis_model,
                        'stage3_projection_model': analysis_model,
                        'pro_model_semaphore_limit': 3,
                        'strategy': 'Flash for extraction, Pro for analysis'
                    },
                    'services_used': {
                        'stage1': 'OCR Service',
                        'stage2': 'Business Analysis Service',
                        'stage3': 'Projection Service'
                    },
                    'api_calls_utilized': total_api_calls,
                    'total_processing_time': total_time,
                    'stage_timings': {
                        'extraction_normalization': stage1_time,
                        'business_analysis': stage2_time,
                        'projection_engine': stage3_time,
                        'local_validation': validation_time
                    },
                    'enhancement_features': [
                        'tiered_model_selection',
                        'concurrency_control',
                        'quota_optimization',
                        'modular_service_architecture',
                        'business_context_analysis',
                        'pattern_recognition', 
                        'methodology_experimentation',
                        'scenario_planning',
                        'financial_reconciliation'
                    ]
                }
            )
            
            logger.info("✅ Enhanced 3-stage modular analysis completed successfully with tiered model selection")
            return response
                
        except HTTPException:
            total_time = time.time() - overall_start_time
            logger.error(f"❌ Analysis failed with HTTPException after {total_time:.2f}s")
            raise
        except Exception as e:
            total_time = time.time() - overall_start_time
            logger.error(f"❌ Analysis failed with unexpected error after {total_time:.2f}s: {str(e)}")
            return MultiPDFAnalysisResponse(
                success=False,
                extracted_data=[],
                normalized_data={},
                projections={},
                explanation="",
                error=f"Enhanced modular analysis failed: {str(e)}",
                data_quality_score=None,
                confidence_levels=None,
                assumptions=None,
                risk_factors=None,
                methodology=None,
                scenarios=None,
                period_granularity=None,
                total_data_points=None,
                time_span=None,
                seasonality_detected=None,
                data_analysis_summary=None
            )
    
    async def analyze_multiple_files(self, files_data: List[Tuple[str, bytes]], requested_model: str = "gemini-2.5-pro") -> MultiPDFAnalysisResponse:
        """
        Enhanced 3-stage multi-file analysis using modular services with tiered model selection
        Applies a 10-minute timeout to the entire process
        """
        try:
            logger.info(f"🚀 Starting multi-file analysis with {self.overall_process_timeout}s overall timeout")
            logger.info(f"🎯 Requested model: {requested_model} | Strategy: Flash for extraction, Pro for analysis")
            
            # Apply overall timeout to the entire analysis process
            result = await asyncio.wait_for(
                self._internal_analyze_multiple_files(files_data, requested_model),
                timeout=self.overall_process_timeout
            )
            
            logger.info("✅ Multi-file analysis completed within timeout")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Overall process timeout exceeded ({self.overall_process_timeout}s)")
            return MultiPDFAnalysisResponse(
                success=False,
                extracted_data=[],
                normalized_data={},
                projections={},
                explanation="",
                error=f"Analysis timeout: Process exceeded {self.overall_process_timeout} seconds limit",
                data_quality_score=None,
                confidence_levels=None,
                assumptions=None,
                risk_factors=None,
                methodology=None,
                scenarios=None,
                period_granularity=None,
                total_data_points=None,
                time_span=None,
                seasonality_detected=None,
                data_analysis_summary=None
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error in multi-file analysis: {str(e)}")
            return MultiPDFAnalysisResponse(
                success=False,
                extracted_data=[],
                normalized_data={},
                projections={},
                explanation="",
                error=f"Analysis failed: {str(e)}",
                data_quality_score=None,
                confidence_levels=None,
                assumptions=None,
                risk_factors=None,
                methodology=None,
                scenarios=None,
                period_granularity=None,
                total_data_points=None,
                time_span=None,
                seasonality_detected=None,
                data_analysis_summary=None
            )

    # Backward compatibility
    async def analyze_multiple_pdfs(self, files_data: List[Tuple[str, bytes]], requested_model: str = "gemini-2.5-pro") -> MultiPDFAnalysisResponse:
        """Backward compatibility method"""
        return await self.analyze_multiple_files(files_data, requested_model)

    def _transform_assumptions(self, assumptions_data: List) -> List[str]:
        """Transform assumption dictionaries into strings for the response model"""
        try:
            if not assumptions_data:
                return []
            
            transformed_assumptions = []
            for assumption in assumptions_data:
                if isinstance(assumption, dict):
                    # Extract the assumption text from the dictionary structure
                    assumption_text = assumption.get('assumption', '')
                    if assumption_text:
                        transformed_assumptions.append(str(assumption_text))
                elif isinstance(assumption, str):
                    # Already a string, use as-is
                    transformed_assumptions.append(assumption)
            
            logger.debug(f"Transformed {len(assumptions_data)} assumption objects into {len(transformed_assumptions)} strings")
            return transformed_assumptions
            
        except Exception as e:
            logger.warning(f"Error transforming assumptions: {str(e)}")
            return []
    
    def _transform_risk_factors(self, risk_factors_data: List) -> List[str]:
        """Transform risk factor data into strings for the response model"""
        try:
            if not risk_factors_data:
                return []
            
            transformed_risks = []
            for risk in risk_factors_data:
                if isinstance(risk, dict):
                    # Extract meaningful text from risk dictionary
                    risk_text = risk.get('risk_factor', risk.get('factor', risk.get('description', str(risk))))
                    if risk_text:
                        transformed_risks.append(str(risk_text))
                elif isinstance(risk, str):
                    transformed_risks.append(risk)
            
            logger.debug(f"Transformed {len(risk_factors_data)} risk factor objects into {len(transformed_risks)} strings")
            return transformed_risks
            
        except Exception as e:
            logger.warning(f"Error transforming risk factors: {str(e)}")
            return []

# Create enhanced service instance
multi_pdf_service = EnhancedMultiPDFService() 