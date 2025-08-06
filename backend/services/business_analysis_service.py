"""
Business Analysis Service - Stage 2: Cash Flow Reconstruction with Enhanced Depreciation
Fixed version with proper cache usage and complete period processing
"""
import asyncio
import time
import json
import json5
import re
import string
import random
from typing import List, Dict, Any, Optional, Union
from fastapi import HTTPException

from google import genai
from google.genai import types
from config import get_next_key, API_KEYS, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY, ENHANCED_CASH_FLOW_CONFIG
from prompts import STAGE2_CASH_FLOW_RECONSTRUCTION_PROMPT
from utils import DataStructureParser, JSONValidator
from logging_config import (get_logger, log_api_call, log_stage_progress, log_token_usage)
import os
from services.enhanced_depreciation import EnhancedDepreciationEstimator, DepreciationEstimate
from services.cash_flow_validator import EnhancedCashFlowValidator, ValidationResult

# Set up logger
logger = get_logger(__name__)

# Only log during main server process, not during uvicorn reloads
if os.getenv("OCR_SERVER_MAIN") == "true":
    logger.info(f"API Configuration: {len(API_KEYS)} keys | Timeout: {API_TIMEOUT}s | Retries: {MAX_RETRIES}")

class EnhancedJSONParser:
    """Enhanced JSON parser with better error handling and validation"""
    
    @staticmethod
    def parse_cash_flow_response(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse cash flow response with multiple strategies and validation
        """
        try:
            if not response_text or not isinstance(response_text, str):
                logger.warning("❌ Empty or invalid response text")
                return None
            
            logger.debug(f"🔧 Parsing cash flow response: {len(response_text)} characters")
            
            # Strategy 1: Direct JSON parsing
            try:
                result = json.loads(response_text.strip())
                if isinstance(result, dict) and EnhancedJSONParser._validate_cash_flow_structure(result):
                    logger.info("✅ Direct JSON parsing successful")
                    return result
            except json.JSONDecodeError:
                logger.debug("⚠️ Direct JSON parsing failed, trying alternatives")
            
            # Strategy 2: Extract from code blocks
            json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            for block in json_blocks:
                try:
                    result = json.loads(block.strip())
                    if isinstance(result, dict) and EnhancedJSONParser._validate_cash_flow_structure(result):
                        logger.info("✅ Code block JSON parsing successful")
                        return result
                except json.JSONDecodeError:
                    continue
            
            # Strategy 3: Find JSON boundaries
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_candidate = response_text[start_idx:end_idx + 1]
                try:
                    result = json.loads(json_candidate)
                    if isinstance(result, dict) and EnhancedJSONParser._validate_cash_flow_structure(result):
                        logger.info("✅ Boundary extraction successful")
                        return result
                except json.JSONDecodeError:
                    logger.debug("⚠️ Boundary extraction failed")
            
            # Strategy 4: JSON5 parsing (more lenient)
            try:
                if start_idx != -1 and end_idx != -1:
                    json_candidate = response_text[start_idx:end_idx + 1]
                    result = json5.loads(json_candidate)
                    if isinstance(result, dict) and EnhancedJSONParser._validate_cash_flow_structure(result):
                        logger.info("✅ JSON5 parsing successful")
                        return result
            except Exception as e:
                logger.debug(f"JSON5 parsing failed: {str(e)}")
            
            logger.error("❌ All parsing strategies failed")
            return None
            
        except Exception as e:
            logger.error(f"❌ Exception in JSON parsing: {str(e)}")
            return None
    
    @staticmethod
    def _validate_cash_flow_structure(data: Dict[str, Any]) -> bool:
        """Validate that parsed data has required cash flow structure"""
        try:
            required_fields = ["version", "currency", "method_version", "periods"]
            
            # Check top-level fields
            for field in required_fields:
                if field not in data:
                    logger.warning(f"❌ Missing required field: {field}")
                    return False
            
            # Check periods structure
            periods = data.get("periods", [])
            if not isinstance(periods, list) or len(periods) == 0:
                logger.warning("❌ No periods found in cash flow data")
                return False
            
            # Validate first period has cash flow fields
            first_period = periods[0]
            required_period_fields = ["period", "ni", "ocf", "delta_cash"]
            
            for field in required_period_fields:
                if field not in first_period:
                    logger.warning(f"❌ Missing required period field: {field}")
                    return False
            
            logger.debug(f"✅ Cash flow structure validation passed with {len(periods)} periods")
            return True
            
        except Exception as e:
            logger.warning(f"❌ Cash flow structure validation failed: {str(e)}")
            return False

class BusinessAnalysisService:
    """Enhanced Service for Stage 2: Cash Flow Reconstruction with Advanced Depreciation and Complete Period Processing"""
    
    def __init__(self):
        # API configuration from config
        self.api_timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        
        # API key pool management
        self.api_key_pool = API_KEYS.copy()
        self.api_key_index = 0
        
        # Enhanced components integration
        self.depreciation_estimator = EnhancedDepreciationEstimator()
        self.cash_flow_validator = EnhancedCashFlowValidator(
            base_tolerance_aud=ENHANCED_CASH_FLOW_CONFIG["quality_validation"]["base_tolerance_aud"],
            base_tolerance_pct=ENHANCED_CASH_FLOW_CONFIG["quality_validation"]["base_tolerance_pct"]
        )
        
        # Configuration
        self.enhanced_config = ENHANCED_CASH_FLOW_CONFIG
        ff = self.enhanced_config.get("feature_flags", {}) if isinstance(self.enhanced_config, dict) else {}
        self.debug_responses = bool(ff.get("enhanced_logging", False))
        
        # Only log during main server process
        if os.getenv("OCR_SERVER_MAIN") == "true":
            logger.info("Enhanced Business Analysis Service (Stage 2) initialized with advanced depreciation and complete period processing")
            logger.info(f"🔧 Enhanced features enabled: {list(ff.keys())}")
        
        logger.debug(f"API configuration | Timeout: {self.api_timeout}s | Max retries: {self.max_retries}")
        logger.debug(f"Enhanced depreciation: {'ENABLED' if bool(ff.get('enhanced_depreciation', False)) else 'DISABLED'}")
        logger.debug(f"Enhanced validation: {'ENABLED' if bool(ff.get('enhanced_validation', False)) else 'DISABLED'}")
    
    def get_next_api_key(self) -> str:
        """Get next API key from pool with rotation"""
        key = self.api_key_pool[self.api_key_index % len(self.api_key_pool)]
        self.api_key_index += 1
        key_preview = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else key[:8] + "..."
        logger.debug(f"API key rotation | Using key: {key_preview} | Position: {self.api_key_index}/{len(self.api_key_pool)}")
        return key
    
    def extract_response_text(self, response) -> str:
        """Extract text from Gemini response"""
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        elif response and hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    text_part = candidate.content.parts[0].text
                    if text_part:
                        return text_part.strip()
        
        raise Exception("No data extracted from Gemini response")
    
    async def handle_rate_limits_with_backoff(self, api_call_func, max_retries: int = 3):
        """Enhanced rate limit handling with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await api_call_func()
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Rate limit hit, backing off {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise e
        raise Exception("Max retries exceeded for rate limiting")

    async def process_with_gemini_cached(self, prompt: str, content: str, model: str, api_key: str,
                                        pnl_cache_key: Optional[str], bs_cache_key: Optional[str],
                                        pnl_periods: int, bs_periods: int,
                                        operation_name: str = "Enhanced Cash Flow Reconstruction") -> str:
        """Process request with Gemini using cached content when available - FIXED VERSION"""
        start_time = time.time()
        last_exception = None
        
        # Calculate expected periods
        expected_periods = max(pnl_periods, bs_periods) if (pnl_periods or bs_periods) else 0
        logger.info(f"📊 Expected periods for cash flow: {expected_periods} (P&L: {pnl_periods}, BS: {bs_periods})")
        
        for attempt in range(self.max_retries + 1):
            try:
                key_suffix = api_key[-4:] if len(api_key) > 4 else "****"
                if attempt == 0:
                    log_api_call(logger, operation_name, model, key_suffix, success=True)
                else:
                    logger.info(f"API call RETRY {attempt}/{self.max_retries}: {operation_name} | Model: {model} | Key: ...{key_suffix}")
                
                # Use new SDK client
                client = genai.Client(api_key=api_key)
                
                # Check if we have valid cache keys and can use cached content
                use_cached_content = (pnl_cache_key and
                                    not pnl_cache_key.startswith("stage1_pnl_cache_not_available") and
                                    not pnl_cache_key.startswith("cache_failed"))
                
                # Enhanced prompt with explicit period requirement
                enhanced_prompt = prompt
                if expected_periods > 0:
                    enhanced_prompt += f"\n\nCRITICAL REQUIREMENT: You MUST generate cash flow data for ALL {expected_periods} periods found in the input data. Each period from the P&L and Balance Sheet MUST have a corresponding cash flow period. Do NOT skip any periods or generate sample data."
                
                if use_cached_content:
                    logger.info(f"🔄 Using cached content for Enhanced Stage 2 | P&L Cache: {pnl_cache_key} | Expected: {expected_periods} periods")
                    
                    # CRITICAL FIX: Properly use cached content
                    response = await self.handle_rate_limits_with_backoff(
                        lambda: asyncio.wait_for(
                            asyncio.to_thread(
                                client.models.generate_content,
                                model=model,
                                contents=enhanced_prompt,  # The prompt with instructions
                                config=types.GenerateContentConfig(
                                    cached_content=pnl_cache_key,  # Properly reference cached content
                                    response_mime_type="application/json"
                                )
                            ),
                            timeout=self.api_timeout
                        )
                    )
                else:
                    logger.info(f"📝 Using standard content approach with enhanced prompt | Expected: {expected_periods} periods")
                    
                    # Fall back to standard content approach with enhanced prompt
                    if content:
                        # Include period expectation in content
                        content_with_expectation = f"EXPECTED_PERIODS: {expected_periods}\n\n{content}"
                        contents = f"{content_with_expectation}\n\n{enhanced_prompt}"
                    else:
                        contents = enhanced_prompt
                    
                    response = await self.handle_rate_limits_with_backoff(
                        lambda: asyncio.wait_for(
                            asyncio.to_thread(
                                client.models.generate_content,
                                model=model,
                                contents=contents,
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json"
                                )
                            ),
                            timeout=self.api_timeout
                        )
                    )
                
                elapsed_time = time.time() - start_time
                response_text = self.extract_response_text(response)

                # Token usage logging per Gemini token docs
                try:
                    usage = getattr(response, "usage_metadata", None)
                    in_tok = getattr(usage, "input_token_count", None) if usage else None
                    out_tok = getattr(usage, "output_token_count", None) if usage else None
                    total_tok = getattr(usage, "total_token_count", None) if usage else None
                    log_token_usage(logger, operation_name, model, in_tok, out_tok, total_tok)
                except Exception:
                    pass
                
                log_api_call(logger, operation_name, model, key_suffix, elapsed_time, success=True)
                
                # Validate we got the expected number of periods
                try:
                    parsed_response = json.loads(response_text)
                    generated_periods = len(parsed_response.get('periods', []))
                    if expected_periods > 0 and generated_periods < expected_periods:
                        logger.warning(f"⚠️ DATA LOSS WARNING: Only {generated_periods}/{expected_periods} periods generated!")
                        # Add warning to response
                        parsed_response['data_quality_warning'] = f"Only {generated_periods} of {expected_periods} periods were processed"
                        response_text = json.dumps(parsed_response)
                    else:
                        logger.info(f"✅ Successfully generated {generated_periods} periods")
                except:
                    pass  # If parsing fails, let the main parser handle it
                
                return response_text
                
            except asyncio.TimeoutError as e:
                elapsed_time = time.time() - start_time
                last_exception = e
                logger.warning(f"API call TIMEOUT: {operation_name} | Attempt {attempt + 1}/{self.max_retries + 1} | Duration: {elapsed_time:.2f}s")
                
                if attempt >= self.max_retries:
                    break
                await asyncio.sleep(self.retry_delay)
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                last_exception = e
                error_str = str(e)
                
                # Check if this is a retryable error
                retryable_errors = [
                    "503 Service Temporarily Unavailable",
                    "502 Bad Gateway",
                    "504 Gateway Timeout",
                    "429 Too Many Requests",
                    "500 Internal Server Error",
                    "500 An internal error has occurred"
                ]
                
                is_retryable = any(error in error_str for error in retryable_errors)
                
                if is_retryable and attempt < self.max_retries:
                    logger.warning(f"API call RETRYABLE ERROR: {operation_name} | Attempt {attempt + 1}/{self.max_retries + 1} | Error: {error_str}")
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"API call NON-RETRYABLE ERROR: {operation_name} | Error: {error_str}")
                    break
        
        # If we reach here, all attempts failed
        elapsed_time = time.time() - start_time
        key_suffix = api_key[-4:] if len(api_key) > 4 else "****"
        final_error = str(last_exception) if last_exception else "Unknown error"
        log_api_call(logger, operation_name, model, key_suffix, elapsed_time, success=False, error=final_error)
        raise last_exception or Exception("All retry attempts failed")
    
    def _extract_stage1_financial_data(self, stage1_results: List[Dict]) -> tuple[Optional[Dict], Optional[Dict], int, int]:
        """Extract P&L and Balance Sheet data from Stage 1 results and count periods"""
        pnl_data = None
        bs_data = None
        pnl_periods = 0
        bs_periods = 0
        
        for result in stage1_results:
            try:
                # Use robust parsing to handle data structure
                normalized_result = DataStructureParser.normalize_stage1_result(result)
                data = normalized_result.get("data", {})
                
                if not data:
                    continue
                
                doc_type = data.get("document_type", "")
                periods = data.get("periods", [])
                
                if doc_type == "Profit and Loss" and not pnl_data:
                    pnl_data = data
                    pnl_periods = len(periods)
                    logger.info(f"✅ P&L data extracted: {pnl_periods} periods")
                elif doc_type == "Balance Sheet" and not bs_data:
                    bs_data = data
                    bs_periods = len(periods)
                    logger.info(f"✅ BS data extracted: {bs_periods} periods")
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract financial data from result: {str(e)}")
                continue
        
        return pnl_data, bs_data, pnl_periods, bs_periods
    
    def _enhance_cash_flow_with_advanced_depreciation(
        self,
        cash_flow_result: Dict[str, Any],
        pnl_data: Optional[Dict[str, Any]],
        bs_data: Optional[Dict[str, Any]],
        expected_periods: int
    ) -> Dict[str, Any]:
        """Enhance cash flow result with advanced depreciation estimation and validation"""
        try:
            ff = self.enhanced_config.get("feature_flags", {})
            if not bool(ff.get("enhanced_depreciation", False)):
                logger.debug("Enhanced depreciation disabled, skipping enhancement")
                return cash_flow_result
            
            logger.info("🔧 Enhancing cash flow with advanced depreciation estimation")
            
            # Get enhanced depreciation estimate
            dep_estimate = self.depreciation_estimator.estimate_depreciation_from_stage1_data(pnl_data, bs_data)
            
            logger.info(f"📊 Depreciation Analysis: Method={dep_estimate.method_used}, "
                       f"Amount=${dep_estimate.monthly_amount:.0f}, Confidence={dep_estimate.confidence:.1%}")
            
            # Update periods with enhanced depreciation
            periods = cash_flow_result.get("periods", [])
            enhanced_periods = []
            
            # Check for data loss
            actual_periods = len(periods)
            if expected_periods > 0 and actual_periods < expected_periods:
                data_loss_pct = ((expected_periods - actual_periods) / expected_periods) * 100
                logger.error(f"⚠️ CRITICAL DATA LOSS: {data_loss_pct:.0f}% of periods missing ({actual_periods}/{expected_periods})")
                cash_flow_result['data_loss_warning'] = {
                    'expected_periods': expected_periods,
                    'actual_periods': actual_periods,
                    'loss_percentage': data_loss_pct,
                    'missing_periods': expected_periods - actual_periods
                }
            
            for period_data in periods:
                enhanced_period = period_data.copy()
                
                # Update depreciation with enhanced estimate
                if dep_estimate.monthly_amount > 0:
                    enhanced_period["depreciation"] = dep_estimate.monthly_amount
                    
                    # Recalculate OCF with new depreciation
                    ni = period_data.get("ni", 0)
                    old_depreciation = period_data.get("depreciation", 0)
                    ocf_adjustment = dep_estimate.monthly_amount - old_depreciation
                    enhanced_period["ocf"] = period_data.get("ocf", 0) + ocf_adjustment
                    
                    # Add enhanced metadata
                    enhanced_period["depreciation_metadata"] = {
                        "method": dep_estimate.method_used,
                        "confidence": dep_estimate.confidence,
                        "original_amount": old_depreciation,
                        "enhanced_amount": dep_estimate.monthly_amount,
                        "adjustment": ocf_adjustment
                    }
                
                # Enhanced validation
                ff = self.enhanced_config.get("feature_flags", {})
                if bool(ff.get("enhanced_validation", False)):
                    validation_result = self.cash_flow_validator.validate_period(enhanced_period, dep_estimate)
                    
                    # Update flags based on enhanced validation
                    enhanced_period["flags"] = validation_result.flags
                    enhanced_period["validation_quality_score"] = validation_result.quality_score
                    
                    # Update reasons with enhanced logic
                    if validation_result.reasons:
                        enhanced_period["reasons"] = validation_result.reasons
                
                enhanced_periods.append(enhanced_period)
            
            # Update cash flow result
            enhanced_result = cash_flow_result.copy()
            enhanced_result["periods"] = enhanced_periods
            
            # Enhanced quality assessment with data loss penalty
            ff = self.enhanced_config.get("feature_flags", {})
            if bool(ff.get("enhanced_validation", False)):
                enhanced_quality = self.cash_flow_validator.validate_full_cash_flow_result(enhanced_result, dep_estimate)
                
                # Apply data loss penalty to quality score
                if expected_periods > 0 and actual_periods < expected_periods:
                    coverage_ratio = actual_periods / expected_periods
                    original_score = enhanced_quality.get('global_score', 0)
                    adjusted_score = original_score * coverage_ratio
                    enhanced_quality['global_score'] = adjusted_score
                    enhanced_quality['data_coverage'] = coverage_ratio
                    enhanced_quality['periods_missing'] = expected_periods - actual_periods
                    logger.info(f"📊 Quality score adjusted for data loss: {original_score:.2f} → {adjusted_score:.2f}")
                
                enhanced_result["quality"] = enhanced_quality
                
                logger.info(f"📊 Enhanced Quality Assessment: Global Score={enhanced_quality.get('global_score', 0):.2f}")
            
            # Add enhancement metadata
            enhanced_result["enhancement_metadata"] = {
                "depreciation_estimation": dep_estimate.to_dict(),
                "enhanced_features_applied": {
                    "advanced_depreciation": True,
                    "enhanced_validation": bool(self.enhanced_config.get("feature_flags", {}).get("enhanced_validation", False)),
                    "progressive_rates": True
                },
                "enhancement_version": "v2.1",
                "data_completeness": {
                    "expected_periods": expected_periods,
                    "actual_periods": actual_periods,
                    "coverage_percentage": (actual_periods / expected_periods * 100) if expected_periods > 0 else 100
                }
            }
            
            logger.info("✅ Cash flow enhancement completed successfully")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ Cash flow enhancement failed: {str(e)}")
            # Return original result if enhancement fails
            return cash_flow_result
    
    async def analyze_business_context(self, stage1_results: List[Dict], model: str = "gemini-2.5-pro", 
                                      pnl_cache_key: Optional[str] = None, 
                                      bs_cache_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced Stage 2: Cash Flow Reconstruction with Advanced Depreciation and Complete Period Processing
        
        Args:
            stage1_results: List of stage 1 extraction results
            model: Model to use for cash flow reconstruction
            pnl_cache_key: P&L cache key for cached content
            bs_cache_key: Balance Sheet cache key for cached content
            
        Returns:
            Enhanced cash flow reconstruction results with advanced depreciation
        """
        try:
            logger.info(f"💰 ENHANCED STAGE 2: Cash Flow Reconstruction ({len(stage1_results)} documents)")
            ff = self.enhanced_config.get("feature_flags", {})
            logger.info(f"🔧 Advanced features: Depreciation={bool(ff.get('enhanced_depreciation', False))}, "
                       f"Validation={bool(ff.get('enhanced_validation', False))}")
            
            api_key = self.get_next_api_key()
            
            # Extract financial data and count periods for enhanced processing
            pnl_data, bs_data, pnl_periods, bs_periods = self._extract_stage1_financial_data(stage1_results)
            expected_periods = max(pnl_periods, bs_periods)
            
            if pnl_data:
                logger.info(f"📊 P&L data available: {pnl_periods} periods")
            else:
                logger.warning("⚠️ No P&L data found - cash flow reconstruction may be limited")
            
            if bs_data:
                logger.info(f"📊 BS data available: {bs_periods} periods")
            else:
                logger.warning("⚠️ No Balance Sheet data found - depreciation estimation may use fallback methods")
            
            logger.info(f"📊 Expected cash flow periods: {expected_periods}")
            
            # Normalize and validate input data using robust parsing
            normalized_documents = []
            for doc_result in stage1_results:
                try:
                    # Use robust parsing to handle data.data structure
                    normalized_doc = DataStructureParser.normalize_stage1_result(doc_result)
                    
                    # Validate the financial data structure
                    if normalized_doc["data"] and JSONValidator.validate_financial_data(normalized_doc["data"]):
                        normalized_documents.append(normalized_doc)
                        logger.debug(f"✅ Document validated: {normalized_doc['filename']}")
                    else:
                        logger.warning(f"❌ Document failed validation: {normalized_doc.get('filename', 'unknown')}")
                        # Still include it but mark as invalid
                        normalized_doc["validation_failed"] = True
                        normalized_documents.append(normalized_doc)
                        
                except Exception as e:
                    logger.error(f"❌ Failed to normalize document: {str(e)}")
                    continue
            
            if not normalized_documents:
                raise ValueError("No valid documents found after normalization")
            
            logger.info(f"📋 Normalized {len(normalized_documents)} documents for analysis")
            
            # Use actual cache keys from Stage 1 or fallback to placeholders
            if not pnl_cache_key:
                pnl_cache_key = "stage1_pnl_cache_not_available"
                logger.warning("⚠️ P&L cache key not provided, using fallback")
            
            if not bs_cache_key:
                bs_cache_key = "stage1_bs_cache_not_available"
                logger.warning("⚠️ BS cache key not provided, using fallback")
            
            logger.info(f"📋 Using cache keys - P&L: {pnl_cache_key}, BS: {bs_cache_key}")
            
            # Enhanced prompt with depreciation context and period requirement
            template = string.Template(STAGE2_CASH_FLOW_RECONSTRUCTION_PROMPT)
            context_prompt = template.substitute(
                pnl_cache_key=pnl_cache_key,
                bs_cache_key=bs_cache_key
            )
            
            # Add explicit period requirement
            context_prompt += f"\n\nCRITICAL DATA COMPLETENESS REQUIREMENT: The input data contains {expected_periods} periods. You MUST generate cash flow data for ALL {expected_periods} periods. Do not skip any periods."
            
            # Add depreciation enhancement context
            ff = self.enhanced_config.get("feature_flags", {})
            if bool(ff.get("enhanced_depreciation", False)) and (pnl_data or bs_data):
                dep_estimate = self.depreciation_estimator.estimate_depreciation_from_stage1_data(pnl_data, bs_data)
                
                depreciation_context = f"""
                
ENHANCED DEPRECIATION ESTIMATION CONTEXT:
Based on Stage 1 data analysis, the recommended depreciation approach is:
- Method: {dep_estimate.method_used}
- Monthly Amount: ${dep_estimate.monthly_amount:.0f}
- Annual Rate: {dep_estimate.annual_rate:.1%}
- Confidence: {dep_estimate.confidence:.1%}
- Justification: {dep_estimate.justification}

Please use this enhanced depreciation estimate in your cash flow reconstruction instead of flat rates.
If you use different amounts, provide clear justification for the variance.
                """
                context_prompt += depreciation_context
                logger.info(f"📊 Enhanced depreciation context added to prompt: ${dep_estimate.monthly_amount:.0f}/month")
            
            # Pass the actual Stage 1 data as content for the prompt
            aggregated_data = {
                "documents": normalized_documents,
                "analysis_request": "Enhanced cash flow reconstruction with advanced depreciation estimation",
                "expected_periods": expected_periods,
                "period_details": {
                    "pnl_periods": pnl_periods,
                    "bs_periods": bs_periods,
                    "total_expected": expected_periods
                }
            }
            stage1_content = json.dumps(aggregated_data, indent=2)
            
            logger.debug(f"📋 Analysis context prepared: {len(context_prompt)} characters")
            
            # Use cached content if available with period tracking
            response = await self.process_with_gemini_cached(
                context_prompt,
                stage1_content,
                model,
                api_key,
                pnl_cache_key,
                bs_cache_key,
                pnl_periods,
                bs_periods,
                "Enhanced Stage 2: Cash Flow Reconstruction"
            )
            
            # Parse response using enhanced JSON parser
            try:
                if self.debug_responses:
                    logger.info(f"🔍 ENHANCED STAGE 2 - Attempting JSON parsing for cash flow reconstruction")
                    logger.info(f"📝 Raw response length: {len(response)} characters")
                    logger.info(f"📋 Raw response preview: {response[:500]}...")
                
                logger.info("🔧 Using EnhancedJSONParser for cash flow response...")
                result = EnhancedJSONParser.parse_cash_flow_response(response)
                
                if result and isinstance(result, dict):
                    # Check for data completeness
                    generated_periods = len(result.get('periods', []))
                    if generated_periods < expected_periods:
                        logger.error(f"⚠️ DATA LOSS DETECTED: Only {generated_periods}/{expected_periods} periods generated!")
                        result['data_loss_detected'] = True
                        result['data_loss_details'] = {
                            'expected': expected_periods,
                            'generated': generated_periods,
                            'missing': expected_periods - generated_periods,
                            'loss_percentage': ((expected_periods - generated_periods) / expected_periods * 100) if expected_periods > 0 else 0
                        }
                    
                    # Apply enhanced depreciation and validation
                    enhanced_result = self._enhance_cash_flow_with_advanced_depreciation(result, pnl_data, bs_data, expected_periods)
                    
                    # Extract key information for logging
                    quality_score = enhanced_result.get('quality', {}).get('global_score', 0)
                    periods_count = len(enhanced_result.get('periods', []))
                    pass_count = enhanced_result.get('quality', {}).get('period_counts', {}).get('pass', 0) if isinstance(enhanced_result.get('quality'), dict) else 0
                    
                    logger.info(f"✅ Enhanced Stage 2 Success: Quality Score: {quality_score:.2f}, "
                               f"Periods: {periods_count}/{expected_periods}, Passed: {pass_count}")
                    
                    return enhanced_result
                else:
                    logger.warning(f"⚠️ EnhancedJSONParser returned invalid result")
                    
            except Exception as parse_error:
                logger.error(f"❌ Exception in enhanced JSON parsing: {str(parse_error)}")
            
            # Enhanced fallback with cash flow schema
            logger.warning("🔄 Generating enhanced fallback structure")
            fallback_result = {
                "version": "1.0",
                "company_id": "unknown_due_to_parsing_error",
                "currency": "AUD",
                "generated_at": "2024-01-01T00:00:00Z",
                "cache_key": "fallback_enhanced_cf_cache_key",
                "parent_keys": {
                    "pnl_cache_key": pnl_cache_key,
                    "bs_cache_key": bs_cache_key
                },
                "method_version": "enhanced_indirect_method_v2.1",
                "remediation_policy_version": "enhanced_standard_v2.1",
                "periods": [],
                "quality": {
                    "global_score": 0.0,  # Zero score for fallback
                    "summary": {
                        "period_counts": {
                            "pass": 0,
                            "warn": 0,
                            "fail": 0
                        },
                        "reconciliation_pass_rate": 0.0,
                        "avg_recon_delta_abs": 0.0
                    },
                    "data_coverage": 0.0,
                    "periods_missing": expected_periods
                },
                "raw_analysis": response,
                "parsing_error": "Enhanced JSON parsing failed - using enhanced fallback structure",
                "enhancement_attempted": True,
                "data_loss_critical": True,
                "expected_periods": expected_periods,
                "actual_periods": 0
            }
            
            # Try to enhance even the fallback
            return self._enhance_cash_flow_with_advanced_depreciation(fallback_result, pnl_data, bs_data, expected_periods)
                
        except Exception as e:
            logger.error(f"❌ Enhanced Stage 2 analysis failed: {str(e)}")
            
            # Return enhanced fallback structure
            enhanced_fallback = {
                "version": "1.0",
                "company_id": "unknown_due_to_exception",
                "currency": "AUD",
                "generated_at": "2024-01-01T00:00:00Z",
                "cache_key": "exception_enhanced_fallback_cf_cache_key",
                "parent_keys": {
                    "pnl_cache_key": "exception_pnl_cache_key",
                    "bs_cache_key": "exception_bs_cache_key"
                },
                "method_version": "enhanced_indirect_method_v2.1",
                "remediation_policy_version": "enhanced_standard_v2.1",
                "periods": [],
                "quality": {
                    "global_score": 0.0,
                    "summary": {
                        "period_counts": {
                            "pass": 0,
                            "warn": 0,
                            "fail": 0
                        },
                        "reconciliation_pass_rate": 0.0,
                        "avg_recon_delta_abs": 0.0
                    },
                    "data_coverage": 0.0,
                    "periods_missing": -1  # Unknown
                },
                "error": str(e),
                "analysis_failed": True,
                "fallback_reason": "Exception in enhanced Stage 2 cash flow reconstruction process",
                "enhancement_attempted": True,
                "data_loss_critical": True
            }
            
            return enhanced_fallback

# Create enhanced business analysis service instance
business_analysis_service = BusinessAnalysisService()