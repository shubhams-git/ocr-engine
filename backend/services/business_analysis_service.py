"""
Business Analysis Service - Stage 2: Business Analysis and Methodology Selection
Separated from multi_pdf_service to create modular stage-based services
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
from config import get_next_key, API_KEYS, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY
from prompts import STAGE2_ANALYSIS_PROMPT
from logging_config import (get_logger, log_api_call, log_stage_progress)
import os

# Set up logger
logger = get_logger(__name__)

# Only log during main server process, not during uvicorn reloads
if os.getenv("OCR_SERVER_MAIN") == "true":
    logger.info(f"API Configuration: {len(API_KEYS)} keys | Timeout: {API_TIMEOUT}s | Retries: {MAX_RETRIES}")

class RobustJSONParser:
    """Robust JSON parser that can handle malformed AI responses"""
    
    @staticmethod
    def clean_and_parse_json(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to parse JSON from potentially malformed AI responses
        Uses multiple strategies to extract valid JSON with enhanced error handling
        """
        try:
            logger.info("🔧 RobustJSONParser: Starting JSON parsing process")
            
            if not response_text:
                logger.warning("❌ Empty or None response text provided to JSON parser")
                return None
                
            if not isinstance(response_text, str):
                logger.warning(f"❌ Invalid response type: {type(response_text)}, expected str")
                return None
            
            original_text = response_text
            original_length = len(original_text)
            logger.info(f"🔧 JSON Parser: Processing {original_length} character response")
            
            # Log the actual content we're trying to parse
            logger.info(f"🔧 JSON Parser: Response starts with: {repr(original_text[:100])}")
            
            # SPECIFIC FIX for the malformed JSON pattern
            # The error '\n  "business_context"' means it's missing the opening brace
            response_text = response_text.strip()
            
            # Strategy 1: Handle missing braces (most common issue)
            if response_text and not response_text.startswith('{') and '"' in response_text:
                logger.info("🔧 Detected missing opening brace - applying fix")
                
                # Add opening brace
                fixed_text = '{' + response_text
                
                # Ensure it ends with closing brace if it doesn't
                if not fixed_text.rstrip().endswith('}'):
                    fixed_text = fixed_text + '}'
                    logger.info("🔧 Also added missing closing brace")
                
                try:
                    result = json.loads(fixed_text)
                    if isinstance(result, dict):
                        logger.info("✅ JSON Parser: Brace fix successful")
                        return result
                except json.JSONDecodeError as e:
                    logger.debug(f"Brace fix failed: {str(e)}")
                    logger.debug(f"Fixed text was: {repr(fixed_text[:200])}")
            
            # Strategy 2: Direct JSON parsing
            try:
                result = json.loads(response_text)
                if isinstance(result, dict):
                    logger.info("✅ JSON Parser: Direct parsing successful")
                    return result
            except json.JSONDecodeError:
                logger.debug("⚠️ JSON Parser: Direct parsing failed")
            except Exception as e:
                logger.debug(f"Direct parsing error: {str(e)}")
            
            # Strategy 3: Extract from markdown code blocks
            try:
                json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', original_text, re.DOTALL)
                if json_blocks:
                    for i, block in enumerate(json_blocks):
                        try:
                            block = block.strip()
                            result = json.loads(block)
                            if isinstance(result, dict):
                                logger.info(f"✅ JSON Parser: Code block parsing successful (block {i+1})")
                                return result
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.debug(f"Code block parsing error: {str(e)}")
                            continue
            except Exception as e:
                logger.debug(f"JSON Parser: Code block extraction failed: {str(e)}")
            
            # Strategy 4: Find JSON object boundaries and extract
            try:
                start_idx = original_text.find('{')
                end_idx = original_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_candidate = original_text[start_idx:end_idx + 1]
                    logger.debug(f"🔧 JSON Parser: Extracted candidate JSON ({len(json_candidate)} chars)")
                    
                    try:
                        result = json.loads(json_candidate)
                        if isinstance(result, dict):
                            logger.info("✅ JSON Parser: Boundary extraction successful")
                            return result
                    except json.JSONDecodeError:
                        logger.debug("JSON Parser: Boundary extraction failed")
                    except Exception as e:
                        logger.debug(f"Boundary extraction error: {str(e)}")
            except Exception as e:
                logger.debug(f"JSON Parser: Boundary extraction error: {str(e)}")
            
            # Strategy 5: Try JSON5 parsing (if available)
            try:
                import json5
                start_idx = original_text.find('{')
                end_idx = original_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    json_candidate = original_text[start_idx:end_idx + 1]
                    result = json5.loads(json_candidate)
                    if isinstance(result, dict):
                        logger.info("✅ JSON Parser: JSON5 parsing successful")
                        return result
            except ImportError:
                logger.debug("JSON5 not available")
            except Exception as e:
                logger.debug(f"JSON Parser: JSON5 parsing failed: {str(e)}")
            
            # Strategy 6: Try to reconstruct from key patterns
            try:
                # Look for business_context and methodology_evaluation patterns
                if '"business_context"' in original_text and '"methodology_evaluation"' in original_text:
                    logger.info("🔧 Attempting pattern-based reconstruction")
                    
                    # Simple reconstruction - wrap the content in braces
                    content = original_text.strip()
                    if not content.startswith('{'):
                        content = '{' + content
                    if not content.endswith('}'):
                        content = content + '}'
                    
                    # Try to fix common issues
                    # Remove trailing commas before closing braces
                    content = re.sub(r',(\s*})', r'\1', content)
                    
                    try:
                        result = json.loads(content)
                        if isinstance(result, dict):
                            logger.info("✅ JSON Parser: Pattern reconstruction successful")
                            return result
                    except json.JSONDecodeError as e:
                        logger.debug(f"Pattern reconstruction failed: {str(e)}")
                        
            except Exception as e:
                logger.debug(f"Pattern reconstruction error: {str(e)}")
            
            logger.error(f"❌ JSON Parser: All parsing strategies failed for {original_length} character response")
            logger.error(f"❌ Response preview: {repr(original_text[:200])}")
            return None
            
        except Exception as e:
            logger.error(f"❌ JSON Parser: Unexpected error in clean_and_parse_json: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    @staticmethod
    def _repair_json_format(text: str) -> Optional[str]:
        """Attempt to repair common JSON formatting issues"""
        try:
            # Remove leading/trailing whitespace and newlines
            text = text.strip()
            
            # If it starts with a quote and field name, try to add opening brace
            if re.match(r'^\s*"[^"]+"\s*:', text):
                text = '{' + text
                logger.debug("🔧 JSON Repair: Added missing opening brace")
            
            # If it ends without closing brace, try to add it
            if not text.rstrip().endswith('}') and '{' in text:
                text = text + '}'
                logger.debug("🔧 JSON Repair: Added missing closing brace")
            
            # Remove trailing commas before closing braces/brackets
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            
            # Fix unescaped quotes in strings
            text = re.sub(r'(?<!\\)"(?![,\s]*[}\]:])(?![^"]*"[^"]*$)', r'\\"', text)
            
            # Remove comments (// or /* */)
            text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
            
            return text
        except Exception as e:
            logger.debug(f"JSON repair error: {str(e)}")
            return None
    
    @staticmethod
    def _extract_json_patterns(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON using pattern matching as last resort"""
        try:
            # Look for key JSON fields that should be in the business analysis response
            patterns = {
                'business_context': r'"business_context"\s*:\s*\{[^}]*\}',
                'methodology_evaluation': r'"methodology_evaluation"\s*:\s*\{[^}]*\}',
                'pattern_analysis': r'"pattern_analysis"\s*:\s*\{[^}]*\}',
                'handover_recommendations': r'"handover_recommendations"\s*:\s*\{[^}]*\}'
            }
            
            extracted_fields = {}
            
            for field_name, pattern in patterns.items():
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    try:
                        field_json = '{' + match.group(0) + '}'
                        field_data = json.loads(field_json)
                        extracted_fields[field_name] = field_data[field_name]
                        logger.debug(f"🔧 Pattern extraction: Found {field_name}")
                    except Exception:
                        continue
            
            if extracted_fields:
                return extracted_fields
                
        except Exception as e:
            logger.debug(f"Pattern extraction error: {str(e)}")
        
        return None

class BusinessAnalysisService:
    """Service for Stage 2: Business Analysis and Methodology Selection"""
    
    def __init__(self):
        # API configuration from config
        self.api_timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        
        # API key pool management
        self.api_key_pool = API_KEYS.copy()
        self.api_key_index = 0
        
        # Debug flag for detailed response logging
        self.debug_responses = False
        
        # Only log during main server process, not during uvicorn reloads
        if os.getenv("OCR_SERVER_MAIN") == "true":
            logger.info("Business Analysis Service (Stage 2) initialized")
        logger.debug(f"API configuration | Timeout: {self.api_timeout}s | Max retries: {self.max_retries} | Retry delay: {self.retry_delay}s")
        logger.debug(f"API key pool initialized | Count: {len(self.api_key_pool)}")
        logger.debug(f"Debug response logging: {'ENABLED' if self.debug_responses else 'DISABLED'}")
    
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
    
    async def process_with_gemini(self, prompt: str, content: str, model: str, api_key: str, operation_name: str = "Business Analysis") -> str:
        """Process single request with Gemini using asyncio with timeout and retry logic"""
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                key_suffix = api_key[-4:] if len(api_key) > 4 else "****"
                if attempt == 0:
                    log_api_call(logger, operation_name, model, key_suffix, success=True)
                else:
                    logger.info(f"API call RETRY {attempt}/{self.max_retries}: {operation_name} | Model: {model} | Key: ...{key_suffix}")
                
                # Use new SDK client
                client = genai.Client(api_key=api_key)
                
                # Create text-based content (Stage 2 works with text analysis)
                if content:
                    contents = f"{content}\n\n{prompt}"
                    logger.debug(f"Request type: text + prompt | Content: {len(content)} chars | Prompt: {len(prompt)} chars")
                else:
                    contents = prompt
                    logger.debug(f"Request type: text-only | Prompt length: {len(prompt)} chars")
                
                # Apply timeout to the API call using new SDK
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=model,
                        contents=contents
                    ),
                    timeout=self.api_timeout
                )
                
                elapsed_time = time.time() - start_time
                response_text = self.extract_response_text(response)
                
                # Log the full raw response for debugging (controlled by debug flag)
                if self.debug_responses:
                    logger.info(f"🔍 RAW RESPONSE from {operation_name}")
                    logger.info(f"📝 Response length: {len(response_text)} characters")
                    logger.info(f"📋 First 200 chars: {response_text[:200]}...")
                    logger.info(f"📋 Last 200 chars: ...{response_text[-200:]}")
                    logger.info(f"📋 FULL RESPONSE:\n{response_text}")
                
                log_api_call(logger, operation_name, model, key_suffix, elapsed_time, success=True)
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
    
    async def analyze_business_context(self, stage1_results: List[Dict], model: str = "gemini-2.5-pro") -> Dict[str, Any]:
        """
        Stage 2: Comprehensive business analysis and methodology selection
        
        Args:
            stage1_results: List of stage 1 extraction results
            model: Model to use for analysis
            
        Returns:
            Dict containing business analysis results and methodology selection
        """
        try:
            logger.info(f"📈 STAGE 2: Business Analysis & Methodology Selection ({len(stage1_results)} documents)")
            
            api_key = self.get_next_api_key()
            
            # Prepare aggregated input
            aggregated_data = {
                "documents": stage1_results,
                "analysis_request": "Comprehensive business intelligence and forecasting methodology selection"
            }
            
            template = string.Template(STAGE2_ANALYSIS_PROMPT)
            context_prompt = template.substitute(
                aggregated_stage1_json=json.dumps(aggregated_data, indent=2)
            )
            
            logger.debug(f"📋 Analysis context prepared: {len(context_prompt)} characters")
            
            response = await self.process_with_gemini(
                context_prompt,
                "",
                model,
                api_key,
                "Stage 2: Business Analysis & Methodology"
            )
            
            # Parse response using robust JSON parser with enhanced error handling
            try:
                if self.debug_responses:
                    logger.info(f"🔍 STAGE 2 - Attempting robust JSON parsing for business analysis")
                    logger.info(f"📝 Raw response length: {len(response)} characters")
                    logger.info(f"📋 Raw response preview: {response[:500]}...")
                    logger.info(f"📋 Raw response (full): {response}")
                
                logger.info("🔧 Calling RobustJSONParser.clean_and_parse_json...")
                result = RobustJSONParser.clean_and_parse_json(response)
                logger.info(f"🔧 RobustJSONParser returned: {type(result)}")
                
                if result and isinstance(result, dict):
                    # Extract key information for logging
                    business_stage = result.get('business_context', {}).get('business_stage', 'N/A')
                    selected_method = result.get('methodology_evaluation', {}).get('selected_method', {}).get('primary_method', 'N/A')
                    logger.info(f"✅ Stage 2 Success: Business Stage: {business_stage}, Method: {selected_method}")
                    return result
                else:
                    logger.warning(f"⚠️ RobustJSONParser returned invalid result: {result}")
                    logger.warning("⚠️ Using enhanced fallback structure")
                    
            except Exception as parse_error:
                logger.error(f"❌ Exception in JSON parsing: {str(parse_error)}")
                logger.error(f"❌ Parse error type: {type(parse_error)}")
                import traceback
                logger.error(f"❌ Parse error traceback: {traceback.format_exc()}")
            
            # Enhanced fallback with original response preserved
            logger.warning("🔄 Generating enhanced fallback structure")
            return {
                "business_context": {
                    "industry_classification": "Unknown", 
                    "business_stage": "growth",
                    "market_geography": "Australian",
                    "competitive_position": "established"
                },
                "methodology_evaluation": {
                    "selected_method": {
                        "primary_method": "ARIMA", 
                        "rationale": "Default selection due to parsing failure",
                        "confidence_level": "low"
                    }
                },
                "handover_recommendations": {
                    "primary_recommendations": ["Use conservative projections due to limited analysis"],
                    "risk_adjustments": ["High uncertainty due to parsing issues"],
                    "scenario_considerations": ["Conservative approach recommended"]
                },
                "raw_analysis": response,
                "parsing_error": "JSON parsing failed - using fallback structure"
            }
                
        except Exception as e:
            logger.error(f"❌ Stage 2 analysis failed with exception: {str(e)}")
            logger.error(f"❌ Exception type: {type(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            
            # Return a comprehensive fallback structure
            return {
                "business_context": {
                    "industry_classification": "Unknown", 
                    "business_stage": "unknown",
                    "market_geography": "Australian",
                    "competitive_position": "unknown"
                },
                "methodology_evaluation": {
                    "selected_method": {
                        "primary_method": "LinearRegression", 
                        "rationale": "Emergency fallback due to analysis failure",
                        "confidence_level": "very_low"
                    }
                },
                "handover_recommendations": {
                    "primary_recommendations": ["Use very conservative projections due to analysis failure"],
                    "risk_adjustments": ["Very high uncertainty due to system error"],
                    "scenario_considerations": ["Emergency fallback - manual review recommended"]
                },
                "error": str(e),
                "analysis_failed": True,
                "fallback_reason": "Exception in Stage 2 analysis process"
            }

# Create business analysis service instance
business_analysis_service = BusinessAnalysisService() 