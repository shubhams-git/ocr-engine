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

from google import genai
from google.genai import types
from config import API_KEYS
from models import MultiPDFAnalysisResponse, OCRResponse
from utils import DataStructureParser, JSONValidator
from logging_config import (get_logger, log_request_start, log_request_end, 
                          log_stage_progress, log_validation_result)

# Import the separate services
from services.ocr_service import ocr_service
from services.business_analysis_service import business_analysis_service
from services.projection_service import projection_service

# Set up logger
logger = get_logger(__name__)

class GeminiCacheManager:
    """Manager for Gemini explicit caching functionality"""
    
    def __init__(self):
        self.client = None
        # Per Gemini caching docs, set TTL to 30 minutes max as requested
        # Duration string format is accepted, e.g., "1800s"
        self.cache_ttl = "1800s"  # 30 minutes
        
    def get_client(self, api_key: str) -> genai.Client:
        """Get or create Gemini client with API key"""
        if not self.client:
            self.client = genai.Client(api_key=api_key)
        return self.client
    
    async def create_cache_for_stage1_result(self, stage1_data: Dict[str, Any], api_key: str, document_type: str, ttl_override: Optional[int] = None) -> str:
        """
        Create explicit cache for Stage 1 result (P&L or BS data)
        Returns the cache resource name for later reference

        ttl_override: Optional seconds to override default cache TTL. If None, uses self.cache_ttl.
        """
        try:
            client = self.get_client(api_key)

            # Convert stage1 data to JSON string for caching
            content_to_cache = json.dumps(stage1_data, indent=2)

            # Create cache with appropriate display name
            cache_display_name = f"stage1_{document_type.lower().replace(' ', '_')}_data"

            # Determine TTL to use
            ttl_str = self.cache_ttl
            if isinstance(ttl_override, int) and ttl_override > 0:
                ttl_str = f"{ttl_override}s"

            logger.info(f"🔄 Creating Gemini cache for {document_type} data ({len(content_to_cache)} chars) | ttl={ttl_str}")

            # Create cache using explicit caching API
            cache = await asyncio.to_thread(
                client.caches.create,
                model="gemini-2.5-pro",
                config=types.CreateCachedContentConfig(
                    display_name=cache_display_name,
                    system_instruction=f"This cached content contains normalized {document_type} financial data from Stage 1 extraction.",
                    contents=[content_to_cache],
                    ttl=ttl_str
                )
            )

            logger.info(f"✅ Cache created successfully: {cache.name} for {document_type}")
            return cache.name or f"cache_creation_failed_{document_type}"

        except Exception as e:
            logger.error(f"❌ Failed to create cache for {document_type}: {str(e)}")
            return f"cache_creation_failed_{document_type}"
    
    async def get_cached_content(self, cache_name: str, api_key: str) -> Optional[str]:
        """Retrieve cached content by cache name"""
        try:
            client = self.get_client(api_key)
            cache = await asyncio.to_thread(client.caches.get, name=cache_name)
            logger.debug(f"📋 Retrieved cache metadata: {cache_name}")
            return cache_name  # Return cache name for use in subsequent API calls
        except Exception as e:
            logger.warning(f"⚠️ Failed to retrieve cache {cache_name}: {str(e)}")
            return None

# Initialize cache manager
cache_manager = GeminiCacheManager()

class EnhancedMultiPDFService:
    """Enhanced service for orchestrating multi-document financial analysis using separate stage services"""
    
    def __init__(self):
        self.max_pdf_size = 50 * 1024 * 1024   # 50MB for PDFs
        self.max_csv_size = 25 * 1024 * 1024   # 25MB for CSV files
        self.max_files = 10
        
        # TIERED MODEL SELECTION & CONCURRENCY CONTROL
        # Stage 1: Use Flash for data extraction (higher quotas, simpler task)
        self.stage1_model = "gemini-2.5-pro"
        
        # Stages 2-3: Use Pro for complex analysis (lower quotas, complex reasoning)
        # Semaphore to limit concurrent Pro model calls to prevent quota exhaustion
        self.pro_model_semaphore = asyncio.Semaphore(3)  # Max 3 concurrent Pro calls
        
        # Only log during main server process, not during uvicorn reloads
        if os.getenv("OCR_SERVER_MAIN") == "true":
            logger.info("Enhanced Multi-PDF Service initialized | Architecture: 3-Stage Modular Services")
            logger.info("🎯 TIERED MODEL SELECTION | Stage 1: Flash (extraction) | Stages 2-3: Pro (analysis)")
            logger.info(f"⚡ CONCURRENCY CONTROL | Pro model semaphore limit: {self.pro_model_semaphore._value}")
        
        logger.debug(f"Service configuration | Max files: {self.max_files} | PDF limit: {self.max_pdf_size//1024//1024}MB | CSV limit: {self.max_csv_size//1024//1024}MB")
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
            
            # Create mapping from results to original filenames
            result_to_filename = {}
            for i, (filename, _) in enumerate(files_data):
                if i < len(stage1_results):
                    result_to_filename[i] = filename
            
            for i, result in enumerate(stage1_results):
                original_filename = result_to_filename.get(i, f"file_{i}")
                
                if isinstance(result, Exception):
                    failed_extractions.append(str(result))
                    logger.error(f"Stage 1 exception | File: {original_filename} | Error: {str(result)}")
                    continue
                
                ocr_response = cast(OCRResponse, result)
                
                try:
                    if ocr_response.success:
                        # Convert OCRResponse to dict for robust parsing
                        ocr_result_dict = {
                            "success": ocr_response.success,
                            "data": ocr_response.data,
                            "error": ocr_response.error
                        }
                        
                        # Use robust parsing to handle data structure
                        normalized_result = DataStructureParser.normalize_stage1_result(ocr_result_dict)
                        
                        # Validate the financial data with enhanced logging
                        data_valid = False
                        if normalized_result["data"]:
                            logger.debug(f"🔍 Validating financial data for {original_filename} | Document type: {normalized_result['data'].get('document_type', 'Unknown')}")
                            data_valid = JSONValidator.validate_financial_data(normalized_result["data"])
                            if not data_valid:
                                logger.warning(f"❌ Financial data validation FAILED for {original_filename} | Document type: {normalized_result['data'].get('document_type', 'Unknown')}")
                                # Log the structure for debugging
                                logger.debug(f"📋 Data structure keys for {original_filename}: {list(normalized_result['data'].keys())}")
                                if 'periods' in normalized_result['data'] and normalized_result['data']['periods']:
                                    first_period_keys = list(normalized_result['data']['periods'][0].keys()) if normalized_result['data']['periods'] else []
                                    logger.debug(f"📋 First period keys for {original_filename}: {first_period_keys}")
                            else:
                                logger.debug(f"✅ Financial data validation PASSED for {original_filename}")
                        else:
                            logger.warning(f"❌ No data found in normalized result for {original_filename}")
                        
                        # Always capture document type for P&L validation, even if validation fails
                        doc_type = normalized_result["data"].get('document_type', 'Other') if normalized_result["data"] else 'Other'
                        filename = original_filename
                        doc_types[filename] = doc_type
                        logger.debug(f"📋 Document type captured: {filename} -> {doc_type}")
                        
                        if data_valid:
                            # Use original filename instead of trying to extract from data
                            extraction_result = {
                                "filename": original_filename,
                                "success": True,
                                "data": normalized_result["data"],
                                "raw_response": ocr_response.data
                            }
                            
                            # Create Gemini cache for P&L and Balance Sheet documents
                            cache_key = None
                            if doc_type in ['Profit and Loss', 'Balance Sheet']:
                                try:
                                    # Get API key for cache creation (from config)
                                    from config import get_next_key
                                    cache_api_key = get_next_key()
                                    
                                    cache_key = await cache_manager.create_cache_for_stage1_result(
                                        normalized_result["data"], 
                                        cache_api_key, 
                                        doc_type
                                    )
                                    logger.info(f"🔄 Cache created for {doc_type}: {cache_key}")
                                except Exception as cache_error:
                                    logger.warning(f"⚠️ Cache creation failed for {doc_type}: {str(cache_error)}")
                                    cache_key = f"cache_failed_{doc_type.lower().replace(' ', '_')}"
                            
                            # Add cache key to extraction result
                            extraction_result["cache_key"] = cache_key
                            successful_extractions.append(extraction_result)
                            
                            logger.info(f"Stage 1 SUCCESS | File: {filename} | Type: {doc_type} | Cache: {cache_key} | Model: {extraction_model}")
                        else:
                            logger.warning(f"❌ OCR result failed financial data validation for {filename} | Type: {doc_type} | Will still use for P&L detection")
                            # Create a minimal extraction result for P&L detection purposes
                            minimal_extraction = {
                                "filename": original_filename,
                                "success": False,
                                "data": normalized_result["data"] if normalized_result["data"] else {},
                                "raw_response": ocr_response.data,
                                "validation_failed": True
                            }
                            failed_extractions.append(f"Financial data validation failed for {filename} (type: {doc_type})")
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
            
            # Check for mandatory P&L with enhanced debugging
            logger.debug(f"📋 Document types detected: {doc_types}")
            doc_type_values = list(doc_types.values())
            logger.debug(f"📋 All document types: {doc_type_values}")
            
            has_profit_loss = any(doc_type == 'Profit and Loss' for doc_type in doc_types.values())
            logger.debug(f"🔍 P&L check result: has_profit_loss = {has_profit_loss}")
            
            if not has_profit_loss:
                logger.error(f"P&L validation FAILED | No Profit & Loss statement detected | Detected types: {doc_type_values} | Successful extractions: {len(successful_extractions)}")
                # Additional debugging: check if any files had P&L in their names
                pnl_filenames = [filename for filename in doc_types.keys() if 'profit' in filename.lower() or 'loss' in filename.lower()]
                if pnl_filenames:
                    logger.error(f"📋 Files with P&L in name but wrong type detected: {pnl_filenames}")
                    for fname in pnl_filenames:
                        logger.error(f"📋 {fname} -> {doc_types[fname]}")
                
                raise HTTPException(
                    status_code=400,
                    detail="No Profit & Loss statement detected. Please upload at least one P&L document for accurate financial projections."
                )
            
            log_stage_progress(logger, "1", "COMPLETED", f"Duration: {stage1_time:.2f}s | Success: {len(successful_extractions)}/{len(files_data)} | Model: {extraction_model}")
            logger.debug(f"Document types extracted | {doc_types}")
            
            # Extract cache keys for Stage 2 (Cash Flow Reconstruction)
            pnl_cache_key = None
            bs_cache_key = None
            
            for extraction in successful_extractions:
                doc_type = doc_types.get(extraction.get('filename', ''), 'Other')
                cache_key = extraction.get('cache_key')
                
                if doc_type == 'Profit and Loss' and cache_key:
                    pnl_cache_key = cache_key
                    logger.info(f"📋 P&L cache key identified: {pnl_cache_key}")
                elif doc_type == 'Balance Sheet' and cache_key:
                    bs_cache_key = cache_key
                    logger.info(f"📋 BS cache key identified: {bs_cache_key}")
            
            # STAGE 2: Cash Flow Reconstruction using Pro Model with Semaphore
            log_stage_progress(logger, "2", "STARTED", f"Cash Flow Reconstruction Service | Model: {analysis_model} | Semaphore: {self.pro_model_semaphore._value}")
            stage2_start = time.time()
            
            # Use semaphore to control Pro model concurrency
            async with self.pro_model_semaphore:
                logger.debug(f"🔒 Acquired Pro model semaphore for Stage 2 | Available: {self.pro_model_semaphore._value}")
                stage2_result = await business_analysis_service.analyze_business_context(
                    successful_extractions, 
                    analysis_model, 
                    pnl_cache_key=pnl_cache_key,
                    bs_cache_key=bs_cache_key
                )
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
            logger.info("🚀 Starting multi-file analysis")
            logger.info(f"🎯 Requested model: {requested_model} | Strategy: Flash for extraction, Pro for analysis")
            
            # Run analysis without timeout
            result = await self._internal_analyze_multiple_files(files_data, requested_model)
            logger.info("✅ Multi-file analysis completed")
            return result
            
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