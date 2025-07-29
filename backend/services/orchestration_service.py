"""
Enhanced Multi-PDF Service - Unified Gemini 2.5 Pro Architecture
UPDATED: All stages now use gemini-2.5-pro with optimized rate limiting
ENHANCED: Smart delay system to prevent 503 overload without excessive delays
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

from config import (
    API_KEYS, OVERALL_PROCESS_TIMEOUT, PRO_MODEL_MIN_DELAY, PRO_MODEL_OVERLOAD_DELAY,
    MAX_RETRIES, BASE_RETRY_DELAY, MAX_RETRY_DELAY, EXPONENTIAL_MULTIPLIER, OVERLOAD_MULTIPLIER
)
from models import MultiPDFAnalysisResponse, OCRResponse
from logging_config import get_logger

# Import the enhanced separate services
from services.extraction_service import extraction_service
from services.cash_flow_service import cash_flow_service
from services.financial_analysis_service import financial_analysis_service
from services.projection_service import projection_service
from services.enhancement_service import enhancement_service

# Set up logger
logger = get_logger(__name__)

class UnifiedProModelService:
    """Enhanced service for orchestrating multi-document financial analysis with UNIFIED PRO MODEL"""
    
    def __init__(self):
        self.max_pdf_size = 50 * 1024 * 1024   # 50MB for PDFs
        self.max_csv_size = 25 * 1024 * 1024   # 25MB for CSV files
        self.max_files = 10
        
        # UNIFIED PRO MODEL CONFIGURATION
        self.unified_model = "gemini-2.5-pro"  # All stages use Pro model
        
        # OPTIMIZED RATE LIMITING - Prevents 503 without excessive delays
        self.pro_model_delay = 12.0  # OPTIMIZED: 12 seconds between Pro calls (was 15s)
        self.pro_overload_delay = 45.0  # OPTIMIZED: 45 seconds after overload (was 60s)
        self.pro_error_delay = 20.0  # OPTIMIZED: 20 seconds after any error (was 30s)
        
        # ENHANCED CONCURRENCY CONTROL
        self.pro_model_semaphore = asyncio.Semaphore(1)  # One Pro call at a time
        
        # SMART TIMING TRACKING
        self.last_pro_request_time = 0
        self.last_pro_overload_time = 0
        self.last_pro_error_time = 0
        
        # Enhanced timeout configuration
        self.overall_process_timeout = OVERALL_PROCESS_TIMEOUT  # 20 minutes
        
        # Only log during main server process, not during uvicorn reloads
        if os.getenv("OCR_SERVER_MAIN") == "true":
            logger.info("🚀 Unified Pro Model Service initialized")
            logger.debug(f"⚙️ Rate limiting: {self.pro_model_delay}s standard | {self.pro_error_delay}s error | {self.pro_overload_delay}s overload")

    async def _acquire_pro_model_with_optimized_delay(self, stage_name: str):
        """Acquire Pro model with optimized delay - reduced logging"""
        current_time = time.time()
        
        # Calculate required delays
        delays = []
        
        # Check overload delay
        if self.last_pro_overload_time > 0:
            time_since_overload = current_time - self.last_pro_overload_time
            if time_since_overload < self.pro_overload_delay:
                delays.append(self.pro_overload_delay - time_since_overload)
        
        # Check error delay  
        if self.last_pro_error_time > 0:
            time_since_error = current_time - self.last_pro_error_time
            if time_since_error < self.pro_error_delay:
                delays.append(self.pro_error_delay - time_since_error)
        
        # Check standard delay
        time_since_last = current_time - self.last_pro_request_time
        if time_since_last < self.pro_model_delay:
            delays.append(self.pro_model_delay - time_since_last)
        
        # Apply maximum delay
        if delays:
            max_delay = max(delays)
            if max_delay > 5:  # Only log significant delays
                logger.info(f"⏱️ Rate limit delay: {max_delay:.1f}s | Stage: {stage_name}")
            await asyncio.sleep(max_delay)
        
        self.last_pro_request_time = time.time()
        await self._acquire_pro_model_semaphore(stage_name)

    async def _acquire_pro_model_semaphore(self, stage_name: str):
        """Acquire Pro model semaphore with minimal logging"""
        try:
            # Use a tiny timeout to simulate a non-blocking acquire
            await asyncio.wait_for(self.pro_model_semaphore.acquire(), timeout=0.01)
            logger.debug(f"🔒 Acquired semaphore | Stage: {stage_name}")
        except asyncio.TimeoutError:
            raise HTTPException(status_code=503, detail="Pro model temporarily unavailable")

    def _release_pro_model_semaphore(self, stage_name: str):
        """Release Pro model semaphore with minimal logging"""
        self.pro_model_semaphore.release()
        logger.debug(f"🔓 Released semaphore | Stage: {stage_name}")

    def _record_pro_error(self, error_type: str = "general"):
        """Record Pro model errors with minimal logging"""
        if "503" in error_type or "overload" in error_type.lower():
            self.last_pro_overload_time = time.time()
            logger.warning(f"🚨 API overload detected | Cooldown: {self.pro_overload_delay}s")
        else:
            self.last_pro_error_time = time.time()
            logger.warning(f"⚠️ API error | Cooldown: {self.pro_error_delay}s")

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
        """Validate files with minimal logging"""
        if not files_data:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files_data) > self.max_files:
            raise HTTPException(status_code=400, detail=f"Too many files. Maximum: {self.max_files}")
        
        for filename, content in files_data:
            file_type, mime_type = self.get_file_type_and_mime(filename, content)
            # Size validation without verbose logging
            if file_type == 'pdf' and len(content) > self.max_pdf_size:
                raise HTTPException(status_code=400, detail=f"PDF too large: {filename}")
            elif file_type == 'csv' and len(content) > self.max_csv_size:
                raise HTTPException(status_code=400, detail=f"CSV too large: {filename}")
        
        logger.info(f"✅ Validated {len(files_data)} files")

    def _count_projection_metrics(self, stage4_result: Dict) -> int:
        """Enhanced projection counting logic to properly count complete projection data"""
        try:
            projections_count = 0
            
            # Check for base_case_projections (primary structure)
            base_case = stage4_result.get('base_case_projections', {})
            if base_case and isinstance(base_case, dict):
                required_metrics = ['revenue', 'expenses', 'gross_profit', 'net_profit']
                required_horizons = ['1_year_ahead', '3_years_ahead', '5_years_ahead', '10_years_ahead', '15_years_ahead']
                
                complete_horizons = 0
                for horizon in required_horizons:
                    if horizon in base_case:
                        horizon_data = base_case[horizon]
                        if isinstance(horizon_data, dict):
                            # Check if all required metrics are present and have data
                            metrics_present = 0
                            for metric in required_metrics:
                                if metric in horizon_data:
                                    metric_data = horizon_data[metric]
                                    if isinstance(metric_data, list) and len(metric_data) > 0:
                                        metrics_present += 1
                            
                            # Count as complete if all 4 metrics are present
                            if metrics_present == 4:
                                complete_horizons += 1
                                projections_count += metrics_present  # Count each metric
                
                logger.info(f"🎯 Projection counting: {complete_horizons} complete horizons, {projections_count} total metrics")
                return projections_count
            
            # Fallback: Check for legacy specific_projections structure
            specific_projections = stage4_result.get('specific_projections', {})
            if specific_projections and isinstance(specific_projections, dict):
                legacy_count = len(specific_projections)
                logger.info(f"🎯 Legacy projection counting: {legacy_count} projections found")
                return legacy_count
            
            # Check if there's any projection-related data
            projection_keywords = ['projection', 'forecast', 'revenue', 'expenses', 'gross_profit', 'net_profit']
            for key, value in stage4_result.items():
                if any(keyword in key.lower() for keyword in projection_keywords):
                    if isinstance(value, (dict, list)) and value:
                        projections_count += 1
            
            logger.info(f"🎯 General projection counting: {projections_count} projection-related items found")
            return projections_count
            
        except Exception as e:
            logger.warning(f"⚠️ Error counting projections: {str(e)}")
            return 0

    async def analyze_multiple_files(self, files_data: List[Tuple[str, bytes]],
                                   model: Optional[str] = None, projection_start_date: str = "2026-01-01") -> MultiPDFAnalysisResponse:
        """
        Main analysis method with reduced logging verbosity
        """
        start_time = time.time()
        unified_model = model or self.unified_model
        
        logger.info(f"🚀 Starting analysis | Files: {len(files_data)} | Model: {unified_model}")
        
        async def _core_analysis():
            # Validate files
            self.validate_files(files_data)
            
            # STAGE 1: Data Extraction
            logger.info("Stage 1: Data extraction started")
            stage1_start = time.time()
            
            stage1_results = []
            for i, (filename, content) in enumerate(files_data):
                try:
                    await self._acquire_pro_model_with_optimized_delay(f"Stage 1 File {i+1}: {filename}")
                    result = await extraction_service.process_extraction(content, filename, unified_model)
                    stage1_results.append(result)
                except Exception as e:
                    self._record_pro_error(str(e))
                    stage1_results.append(e)
                    logger.error(f"❌ Stage 1 File {i+1} FAILED: {filename} | Error: {str(e)}")
                finally:
                    self._release_pro_model_semaphore(f"Stage 1 File {i+1}: {filename}")
            
            stage1_time = time.time() - stage1_start
            
            successful_extractions, failed_extractions, doc_types = [], [], {}
            for result in stage1_results:
                if isinstance(result, Exception):
                    failed_extractions.append(str(result))
                    continue
                ocr_response = cast(OCRResponse, result)
                try:
                    if ocr_response.success:
                        parsed_data = json.loads(ocr_response.data) if isinstance(ocr_response.data, str) else ocr_response.data
                        extraction_result = {"filename": parsed_data.get('source_filename', 'Unknown'), "success": True, "data": parsed_data, "raw_response": ocr_response.data}
                        successful_extractions.append(extraction_result)
                        doc_types[extraction_result.get('filename', 'Unknown')] = parsed_data.get('document_type', 'Other')
                    else:
                        failed_extractions.append(ocr_response.error or 'Unknown error')
                except (json.JSONDecodeError, AttributeError) as e:
                    failed_extractions.append(f"Processing error: {str(e)}")
            
            if not successful_extractions:
                raise HTTPException(status_code=500, detail=f"Data extraction failed for all files. Errors: {failed_extractions}")
            if not any(doc_type == 'Profit and Loss' for doc_type in doc_types.values()):
                raise HTTPException(status_code=400, detail="No Profit & Loss statement detected. Please upload at least one P&L document.")
            
            logger.info(f"Stage 1: ✅ Complete | {stage1_time:.1f}s | Success: {len(successful_extractions)}/{len(files_data)}")
            
            # STAGE 2: Cash Flow
            logger.info("Stage 2: Cash flow analysis started")
            stage2_start = time.time()
            try:
                await self._acquire_pro_model_with_optimized_delay("Stage 2")
                stage2_result = await cash_flow_service.generate_cash_flows_and_analyze(successful_extractions, unified_model)
            finally:
                self._release_pro_model_semaphore("Stage 2")
            stage2_time = time.time() - stage2_start
            business_stage = stage2_result.get('business_context', {}).get('business_stage', 'Unknown')
            logger.info(f"Stage 2: ✅ Complete | {stage2_time:.1f}s | Business: {business_stage}")
            
            # STAGE 3: Analysis
            logger.info("Stage 3: Financial analysis started")
            stage3_start = time.time()
            try:
                await self._acquire_pro_model_with_optimized_delay("Stage 3")
                stage3_result = await financial_analysis_service.analyze_comprehensive_business_context(stage2_result, unified_model)
            finally:
                self._release_pro_model_semaphore("Stage 3")
            stage3_time = time.time() - stage3_start
            logger.info(f"Stage 3: ✅ Complete | {stage3_time:.1f}s")

            # STAGE 3.5: Enhancement
            logger.info("Stage 3.5: Strategic enhancement started")
            stage3_5_start = time.time()
            try:
                await self._acquire_pro_model_with_optimized_delay("Stage 3.5")
                stage3_5_result = await enhancement_service.enhance_analysis(stage3_result, unified_model)
            finally:
                self._release_pro_model_semaphore("Stage 3.5")
            stage3_5_time = time.time() - stage3_5_start
            logger.info(f"Stage 3.5: ✅ Complete | {stage3_5_time:.1f}s")
            
            # STAGE 4: Projections
            logger.info("Stage 4: Projections started")
            stage4_start = time.time()
            try:
                await self._acquire_pro_model_with_optimized_delay("Stage 4")
                stage4_result = await projection_service.generate_projections(stage3_5_result, unified_model)
            finally:
                self._release_pro_model_semaphore("Stage 4")
            stage4_time = time.time() - stage4_start
            projections_count = self._count_projection_metrics(stage4_result)
            logger.info(f"Stage 4: ✅ Complete | {stage4_time:.1f}s | Projections: {projections_count}")
            
            total_time = time.time() - start_time
            
            # Check for fallback generation in Stage 4
            is_successful = True
            error_message = None
            if stage4_result.get("fallback_generation_used"):
                is_successful = False
                error_message = "Projection generation failed and fallback data was used."
                logger.warning(f"🚨 {error_message}")

            logger.info(f"🎉 Analysis complete | Total: {total_time:.1f}s | Success: {is_successful}")
            
            # Assemble comprehensive response
            return MultiPDFAnalysisResponse(
                success=is_successful,
                extracted_data=successful_extractions,
                normalized_data=stage2_result,
                projections=stage4_result,
                explanation=stage4_result.get('executive_summary', 'Enhanced 4-stage financial analysis completed.'),
                error=error_message,
                data_quality_score=1.0, # Simplified
                confidence_levels=projection_service.get_confidence_levels(stage4_result),
                assumptions=self._transform_assumptions(stage4_result.get('assumption_documentation', {}).get('critical_assumptions', [])),
                risk_factors=self._transform_risk_factors(stage3_result.get('integrated_scenario_framework', {}).get('scenario_variable_relationships', [])),
                methodology=projection_service.get_methodology_string(stage4_result),
                scenarios=stage4_result.get('scenario_projections', {}),
                period_granularity=successful_extractions[0].get('data', {}).get('basic_context', {}).get('reporting_frequency', 'monthly') if successful_extractions else 'monthly',
                total_data_points=sum(result.get('data', {}).get('data_quality_assessment', {}).get('total_periods', 0) for result in successful_extractions),
                time_span=f"Multi-document analysis spanning {len(successful_extractions)} documents",
                seasonality_detected=stage2_result.get('contextual_analysis', {}).get('seasonality_patterns', {}).get('seasonal_detected', False),
                data_analysis_summary={'document_types': doc_types} # Simplified
            )

        try:
            return await asyncio.wait_for(_core_analysis(), timeout=self.overall_process_timeout)
        except asyncio.TimeoutError:
            logger.error(f"❌ Analysis timeout after {(time.time() - start_time):.1f}s")
            raise HTTPException(status_code=408, detail="Analysis timeout - process took too long")
        except Exception as e:
            logger.error(f"❌ Analysis failed | Error: {str(e)}")
            raise

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
                    assumption_text = assumption.get('assumption', '')
                    if assumption_text:
                        transformed_assumptions.append(str(assumption_text))
                elif isinstance(assumption, str):
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

# Create unified service instance
orchestration_service = UnifiedProModelService()