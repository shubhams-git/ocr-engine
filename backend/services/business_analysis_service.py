"""
Enhanced Business Analysis Service - Stage 2: Business Analysis with Smart Pro Model Fallback
Implements intelligent cooldown periods and Flash model fallback after 2nd retry
UPDATED: Now uses SuperRobustJSONParser and IntelligentMethodologySelector
"""
import asyncio
import time
import json
import json5
import re
import string
from typing import List, Dict, Any, Optional, Union
from fastapi import HTTPException

from google import genai
from config import (
    get_next_key, API_KEYS, API_TIMEOUT, MAX_RETRIES, BASE_RETRY_DELAY,
    MAX_RETRY_DELAY, EXPONENTIAL_MULTIPLIER, OVERLOAD_MULTIPLIER,
    PRO_MODEL_MIN_DELAY, PRO_MODEL_ERROR_DELAY, PRO_MODEL_OVERLOAD_DELAY, 
    FLASH_FALLBACK_THRESHOLD,
    calculate_smart_backoff_delay, get_fallback_model, enhance_prompt_for_flash_fallback
)
from prompts import STAGE2_CASH_FLOW_PROMPT
from logging_config import (get_logger, log_api_call, log_stage_progress)
import os
from .utils import SuperRobustJSONParser, IntelligentMethodologySelector

# Set up logger
logger = get_logger(__name__)

# SMART GLOBAL RATE LIMITER - Enhanced with Error Tracking
class SmartGlobalRateLimiter:
    """Smart global rate limiter with Pro model protection and error tracking"""
    
    def __init__(self):
        self.flash_min_delay = 2.5  # 2.5s for Flash model
        self.pro_min_delay = PRO_MODEL_MIN_DELAY  # 15s base for Pro model
        self.pro_error_delay = PRO_MODEL_ERROR_DELAY  # 30s after any error
        self.pro_overload_delay = PRO_MODEL_OVERLOAD_DELAY  # 60s after overload
        
        self.last_flash_request_time = 0
        self.last_pro_request_time = 0
        self.last_pro_error_time = 0
        self.last_pro_overload_time = 0
        
        self.lock = asyncio.Lock()
    
    async def acquire_flash(self, operation_name: str = "Flash API"):
        """Acquire rate limit for Flash model calls"""
        async with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_flash_request_time
            
            if time_since_last < self.flash_min_delay:
                sleep_time = self.flash_min_delay - time_since_last
                logger.debug(f"🕐 Flash rate limit: Waiting {sleep_time:.2f}s before {operation_name}")
                await asyncio.sleep(sleep_time)
            
            self.last_flash_request_time = time.time()
            logger.debug(f"✅ Flash rate limit acquired for {operation_name}")
    
    async def acquire_pro(self, operation_name: str = "Pro API"):
        """Acquire rate limit for Pro model calls with smart protection"""
        async with self.lock:
            current_time = time.time()
            delays_to_check = []
            
            # Check overload delay (highest priority)
            time_since_overload = current_time - self.last_pro_overload_time
            if time_since_overload < self.pro_overload_delay:
                delays_to_check.append(("overload protection", self.pro_overload_delay - time_since_overload))
            
            # Check error delay (medium priority)
            time_since_error = current_time - self.last_pro_error_time
            if time_since_error < self.pro_error_delay:
                delays_to_check.append(("error protection", self.pro_error_delay - time_since_error))
            
            # Check standard delay (lowest priority)
            time_since_last = current_time - self.last_pro_request_time
            if time_since_last < self.pro_min_delay:
                delays_to_check.append(("standard rate limit", self.pro_min_delay - time_since_last))
            
            # Apply the longest delay
            if delays_to_check:
                delay_reason, delay_time = max(delays_to_check, key=lambda x: x[1])
                logger.info(f"🕐 Pro model {delay_reason}: Waiting {delay_time:.1f}s before {operation_name}")
                await asyncio.sleep(delay_time)
            
            self.last_pro_request_time = time.time()
            logger.info(f"✅ Pro rate limit acquired for {operation_name}")
    
    def record_pro_error(self):
        """Record when any Pro model error occurred"""
        self.last_pro_error_time = time.time()
        logger.debug(f"📝 Pro model error recorded - will wait {self.pro_error_delay}s before next Pro call")
    
    def record_pro_overload(self):
        """Record when a Pro model overload occurred"""
        self.last_pro_overload_time = time.time()
        logger.warning(f"🚨 Pro model overload recorded - will wait {self.pro_overload_delay}s before next Pro call")

# Create smart global rate limiter instance
smart_global_rate_limiter = SmartGlobalRateLimiter()

class BusinessAnalysisService:
    """Enhanced Service for Stage 2: Business Analysis with Smart Pro Model Fallback"""
    
    def __init__(self):
        # API configuration from enhanced config
        self.api_timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.base_retry_delay = BASE_RETRY_DELAY
        self.max_retry_delay = MAX_RETRY_DELAY
        self.exponential_multiplier = EXPONENTIAL_MULTIPLIER
        self.overload_multiplier = OVERLOAD_MULTIPLIER
        self.flash_fallback_threshold = FLASH_FALLBACK_THRESHOLD
        
        # Debug flag for detailed response logging
        self.debug_responses = False
        
        # Only log during main server process, not during uvicorn reloads
        if os.getenv("OCR_SERVER_MAIN") == "true":
            logger.info("Enhanced Business Analysis Service (Stage 2) initialized with SMART PRO MODEL FALLBACK")
            logger.info(f"SMART FALLBACK: Max retries: {self.max_retries} | Base delay: {self.base_retry_delay}s | Max delay: {self.max_retry_delay}s")
            logger.info(f"FALLBACK STRATEGY: Pro model attempts 1-{self.flash_fallback_threshold-1}, Flash fallback from attempt {self.flash_fallback_threshold}")
            logger.info(f"PRO PROTECTION: Min: {PRO_MODEL_MIN_DELAY}s | Error: {PRO_MODEL_ERROR_DELAY}s | Overload: {PRO_MODEL_OVERLOAD_DELAY}s")
            logger.info("UPDATED: Now using SuperRobustJSONParser and IntelligentMethodologySelector")
        
        logger.debug(f"Enhanced API configuration | Timeout: DISABLED | Max retries: {self.max_retries}")
        logger.debug(f"Smart backoff | Base: {self.base_retry_delay}s | Max: {self.max_retry_delay}s | Multiplier: {self.exponential_multiplier}x")
        logger.debug(f"API key pool available | Count: {len(API_KEYS)}")
    
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
    
    async def process_with_gemini_smart_fallback(self, prompt: str, content: str, original_model: str, operation_name: str = "Business Analysis") -> str:
        """Process request with Gemini using SMART PRO MODEL FALLBACK"""
        start_time = time.time()
        last_exception = None
        had_previous_error = False
        # Initialize to safe defaults to satisfy static analysis and ensure logging safety
        current_model = original_model
        is_fallback = False
        is_pro_model = "pro" in (current_model.lower() if isinstance(current_model, str) else "")
        
        for attempt in range(self.max_retries + 1):
            try:
                # SMART FALLBACK: Determine which model to use
                current_model = get_fallback_model(original_model, attempt)
                is_fallback = current_model != original_model
                is_pro_model = "pro" in current_model.lower()
                
                # SMART RATE LIMITING
                if is_pro_model:
                    await smart_global_rate_limiter.acquire_pro(f"{operation_name} (Attempt {attempt + 1})")
                else:
                    await smart_global_rate_limiter.acquire_flash(f"{operation_name} (Attempt {attempt + 1})")
                
                # GET FRESH API KEY FOR EACH ATTEMPT
                api_key = get_next_key()
                key_suffix = api_key[-4:] if len(api_key) > 4 else "****"
                
                if attempt == 0:
                    log_api_call(logger, operation_name, current_model, key_suffix, success=True)
                else:
                    fallback_info = " (FLASH FALLBACK)" if is_fallback else ""
                    safe_model = current_model if isinstance(current_model, str) else original_model
                    logger.info(f"🔄 API call RETRY {attempt}/{self.max_retries}: {operation_name} | Model: {safe_model}{fallback_info} | Key: ...{key_suffix}")
                
                # ENHANCE PROMPT FOR FLASH FALLBACK
                current_prompt = prompt
                if is_fallback:
                    current_prompt = enhance_prompt_for_flash_fallback(prompt, "Stage 2: Business Analysis")
                    logger.info(f"🔧 Enhanced prompt for Flash fallback ({len(current_prompt)} chars)")
                
                # Use new SDK client with fresh key
                client = genai.Client(api_key=api_key)
                
                # Create text-based content
                if content:
                    contents = f"{content}\n\n{current_prompt}"
                    logger.debug(f"Request type: text + prompt | Content: {len(content)} chars | Prompt: {len(current_prompt)} chars")
                else:
                    contents = current_prompt
                    logger.debug(f"Request type: text-only | Prompt length: {len(current_prompt)} chars")
                
                # Count tokens before making the request
                try:
                    token_info = await asyncio.to_thread(
                        client.models.count_tokens,
                        model=current_model,
                        contents=contents
                    )
                    prompt_tokens = getattr(token_info, "total_tokens", None) or getattr(token_info, "usage_metadata", {}).get("total_tokens", None)
                except Exception as _token_err:
                    prompt_tokens = None
                    logger.debug(f"Token count unavailable: {str(_token_err)}")
                
                # Make API call without timeout
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=current_model,
                    contents=contents
                )
                
                elapsed_time = time.time() - start_time
                response_text = self.extract_response_text(response)
                
                # Attempt to read response usage if available
                response_tokens = None
                try:
                    usage_meta = getattr(response, "usage_metadata", None)
                    if usage_meta and hasattr(usage_meta, "candidates_token_count"):
                        response_tokens = getattr(usage_meta, "candidates_token_count", None)
                except Exception:
                    response_tokens = None
                
                # Log token summary
                if prompt_tokens is not None or response_tokens is not None:
                    logger.info(f"🧮 Tokens | prompt={prompt_tokens if prompt_tokens is not None else 'n/a'} | response={response_tokens if response_tokens is not None else 'n/a'}")
                
                # Log success
                success_info = " with FLASH FALLBACK" if is_fallback else ""
                log_api_call(logger, operation_name, current_model, key_suffix, elapsed_time, success=True)
                logger.info(f"✅ {operation_name} SUCCESS{success_info} after {attempt + 1} attempts in {elapsed_time:.2f}s")
                return response_text
                
            except asyncio.TimeoutError as e:
                # Timeouts disabled; treat as generic error path
                elapsed_time = time.time() - start_time
                last_exception = e
                had_previous_error = True
                is_pro = bool(isinstance(is_pro_model, bool) and is_pro_model)
                if is_pro:
                    smart_global_rate_limiter.record_pro_error()
                logger.warning(f"⏰ Timeout encountered but timeouts are disabled | Duration: {elapsed_time:.2f}s")
                if attempt >= self.max_retries:
                    break
                delay = calculate_smart_backoff_delay(attempt, self.base_retry_delay, is_overload=False, had_previous_error=True)
                logger.info(f"⏳ Retry delay after pseudo-timeout: {delay:.1f}s")
                await asyncio.sleep(delay)
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                last_exception = e
                had_previous_error = True
                error_str = str(e)
                
                # Enhanced overload detection
                is_503_overload = any(indicator in error_str for indicator in [
                    "503 UNAVAILABLE",
                    "503 Service Temporarily Unavailable",
                    "503 Service Unavailable",
                    "The model is overloaded",
                    "model is overloaded",
                    "overloaded",
                    "RESOURCE_EXHAUSTED"
                ])
                
                # Other retryable errors
                other_retryable = any(indicator in error_str for indicator in [
                    "502 Bad Gateway",
                    "504 Gateway Timeout", 
                    "429 Too Many Requests",
                    "500 Internal Server Error"
                ])
                
                # Record errors for Pro models
                if is_pro_model:
                    if is_503_overload:
                        smart_global_rate_limiter.record_pro_overload()
                    else:
                        smart_global_rate_limiter.record_pro_error()
                
                is_retryable = is_503_overload or other_retryable
                
                if is_retryable and attempt < self.max_retries:
                    if is_503_overload:
                        # Smart backoff with overload handling
                        delay = calculate_smart_backoff_delay(attempt, self.base_retry_delay, is_overload=True, had_previous_error=True)
                        logger.warning(f"🚨 503 OVERLOAD detected - using smart backoff: {delay:.1f}s")
                        safe_model = current_model if isinstance(current_model, str) else original_model
                        logger.warning(f"🔄 Overload retry {attempt + 1}/{self.max_retries}: {operation_name} | Model: {safe_model} | Error: {error_str[:100]}...")
                    else:
                        # Standard smart backoff
                        delay = calculate_smart_backoff_delay(attempt, self.base_retry_delay, is_overload=False, had_previous_error=True)
                        logger.warning(f"🔄 Retryable error - smart backoff: {delay:.1f}s")
                        logger.warning(f"🔄 Retry {attempt + 1}/{self.max_retries}: {operation_name} | Error: {error_str[:100]}...")
                    
                    logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"❌ NON-RETRYABLE ERROR or max retries exceeded: {operation_name} | Error: {error_str}")
                    break
        
        # All attempts failed
        elapsed_time = time.time() - start_time
        final_error = str(last_exception) if last_exception else "Unknown error"
        log_api_call(logger, operation_name, "FAILED", "FAILED", elapsed_time, success=False, error=final_error)
        logger.error(f"❌ {operation_name} FAILED after {self.max_retries + 1} attempts in {elapsed_time:.2f}s")
        raise last_exception or Exception(f"All {self.max_retries + 1} retry attempts failed")
    
    async def generate_cash_flows_and_analyze(self, stage1_results: List[Dict], model: str = "gemini-2.5-pro") -> Dict[str, Any]:
        """
        Stage 2: Enhanced Cash Flow Generation & Business Analysis with Smart Pro Model Fallback
        UPDATED: Now uses SuperRobustJSONParser and IntelligentMethodologySelector
        """
        try:
            logger.info(f"💰 STAGE 2: Enhanced Cash Flow Generation & Business Analysis with SUPER ROBUST JSON PARSER ({len(stage1_results)} documents)")
            logger.info(f"🎯 Model: {model} | Max retries: {self.max_retries} | Base delay: {self.base_retry_delay}s | Max delay: {self.max_retry_delay}s")
            logger.info(f"🔄 SMART FALLBACK: Pro attempts 1-{self.flash_fallback_threshold-1}, Flash fallback from attempt {self.flash_fallback_threshold}")
            logger.info("🔧 UPDATED: Using SuperRobustJSONParser with 8 parsing strategies")
            
            # Prepare stage1 standard field data for cash flow reconstruction
            stage1_standard_field_data = {
                "standard_field_mappings": [],
                "raw_extractions": stage1_results
            }
            
            # Extract standard field mappings from each document
            for result in stage1_results:
                if result.get('success') and result.get('data'):
                    try:
                        data = result['data']
                        if isinstance(data, str):
                            data = json.loads(data)
                        
                        standard_fields = data.get('standard_field_mapping', {})
                        if standard_fields:
                            stage1_standard_field_data["standard_field_mappings"].append({
                                "filename": result.get('filename', 'unknown'),
                                "document_type": data.get('document_type', 'unknown'),
                                "standard_fields": standard_fields,
                                "data_quality": data.get('data_quality_assessment', {}),
                                "legacy_normalized_data": data.get('legacy_normalized_time_series', {})
                            })
                    except Exception as e:
                        logger.warning(f"Error processing document {result.get('filename', 'unknown')}: {str(e)}")
            
            # Template processing with error handling
            try:
                template = string.Template(STAGE2_CASH_FLOW_PROMPT)
                context_prompt = template.safe_substitute(
                    stage1_standard_field_data=json.dumps(stage1_standard_field_data, indent=2)
                )
            except Exception as template_error:
                logger.error(f"❌ Template substitution failed: {str(template_error)}")
                try:
                    data_json = json.dumps(stage1_standard_field_data, indent=2)
                    context_prompt = STAGE2_CASH_FLOW_PROMPT.replace('$stage1_standard_field_data', data_json)
                    logger.info("✅ Used fallback string replacement for template")
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback template replacement also failed: {str(fallback_error)}")
                    context_prompt = f"""
Analyze the following financial data and provide cash flow generation and business analysis.

DATA:
{json.dumps(stage1_standard_field_data, indent=2)}

Please provide a JSON response with business context, methodology evaluation, and comprehensive handover recommendations.
"""
                    logger.warning("⚠️ Using simplified fallback prompt due to template issues")
            
            logger.debug(f"📋 Enhanced cash flow generation context prepared: {len(context_prompt)} characters")
            
            # USE SMART PRO MODEL FALLBACK METHOD
            response = await self.process_with_gemini_smart_fallback(
                context_prompt,
                "",
                model,
                "Stage 2: Enhanced Cash Flow Generation & Business Analysis"
            )
            
            # UPDATED: Use SuperRobustJSONParser instead of old parser
            try:
                if self.debug_responses:
                    logger.info(f"🔍 STAGE 2 - Using SuperRobustJSONParser with 8 parsing strategies")
                    logger.info(f"📝 Raw response length: {len(response)} characters")
                    logger.info(f"📋 Raw response preview: {response[:500]}...")
                
                logger.info("🔧 Calling SuperRobustJSONParser.parse_gemini_response...")
                result = SuperRobustJSONParser.parse_gemini_response(response)
                logger.info(f"🔧 SuperRobustJSONParser returned: {type(result)}")
                
                if result and isinstance(result, dict):
                    # Extract key information for logging
                    business_stage = result.get('business_context', {}).get('business_stage', 'N/A')
                    selected_method = result.get('methodology_evaluation', {}).get('selected_method', {}).get('primary_method', 'N/A')
                    logger.info(f"✅ Stage 2 Success with SUPER ROBUST JSON PARSER: Business Stage: {business_stage}, Method: {selected_method}")
                    return result
                else:
                    logger.warning(f"⚠️ SuperRobustJSONParser returned invalid result: {result}")
                    logger.warning("⚠️ Using intelligent fallback structure")
                    
            except Exception as parse_error:
                logger.error(f"❌ Exception in SuperRobustJSONParser: {str(parse_error)}")
                import traceback
                logger.error(f"❌ Parse error traceback: {traceback.format_exc()}")
            
            # UPDATED: Enhanced fallback with intelligent methodology selection
            logger.warning("🔄 Generating intelligent fallback structure with SuperRobustJSONParser")
            
            # Use intelligent methodology selector instead of hardcoded ARIMA
            methodology = IntelligentMethodologySelector.select_optimal_methodology(stage1_standard_field_data)
            
            return {
                "business_context": {
                    "industry_classification": "Unknown", 
                    "business_stage": "growth",
                    "market_geography": "Australian",
                    "competitive_position": "established"
                },
                "methodology_evaluation": {
                    "selected_method": {
                        "primary_method": methodology["primary_method"],
                        "rationale": f"Intelligent selection due to parsing failure: {methodology['rationale']}", 
                        "confidence_level": methodology["confidence_level"]
                    }
                },
                "handover_recommendations": {
                    "primary_recommendations": [f"Use {methodology['primary_method']} methodology selected based on data characteristics"],
                    "risk_adjustments": ["Medium uncertainty due to parsing issues but intelligent methodology selected"],
                    "scenario_considerations": [f"Apply {methodology['primary_method']} with {methodology['confidence_level']} confidence"]
                },
                "raw_analysis": response,
                "parsing_error": "SuperRobustJSONParser failed - using intelligent methodology selection",
                "super_robust_parser_used": True,
                "intelligent_methodology_selection": methodology
            }
                
        except Exception as e:
            logger.error(f"❌ Stage 2 enhanced analysis failed with exception: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            
            # UPDATED: Return comprehensive fallback structure with intelligent methodology
            methodology = IntelligentMethodologySelector.select_optimal_methodology({})
            
            return {
                "business_context": {
                    "industry_classification": "Unknown", 
                    "business_stage": "unknown",
                    "market_geography": "Australian",
                    "competitive_position": "unknown"
                },
                "methodology_evaluation": {
                    "selected_method": {
                        "primary_method": methodology["primary_method"],
                        "rationale": f"Emergency fallback due to analysis failure: {methodology['rationale']}",
                        "confidence_level": methodology["confidence_level"]
                    }
                },
                "handover_recommendations": {
                    "primary_recommendations": [f"Use very conservative projections with {methodology['primary_method']} due to system failure"],
                    "risk_adjustments": ["Very high uncertainty due to system error"],
                    "scenario_considerations": [f"Emergency fallback - manual review recommended with {methodology['primary_method']}"]
                },
                "error": str(e),
                "analysis_failed": True,
                "fallback_reason": "Exception in Stage 2 enhanced analysis process",
                "super_robust_parser_used": True,
                "intelligent_methodology_selection": methodology
            }

# Create enhanced business analysis service instance
business_analysis_service = BusinessAnalysisService()