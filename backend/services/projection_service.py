"""
Projection Service - Stage 3: Projection Engine with Scenario Planning
Separated from multi_pdf_service to create modular stage-based services
"""
import asyncio
import time
import json
import re
import string
from typing import Dict, Any
from fastapi import HTTPException

from google import genai
from config import get_next_key, API_KEYS, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY
from prompts import STAGE3_PROJECTION_PROMPT
from logging_config import (get_logger, log_api_call, log_stage_progress)

# Set up logger
logger = get_logger(__name__)

class ProjectionService:
    """Service for Stage 3: Projection Engine with Scenario Planning"""
    
    def __init__(self):
        # API configuration from config
        self.api_timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        
        # API key pool management
        self.api_key_pool = API_KEYS.copy()
        self.api_key_index = 0
        
        # Debug flag for detailed response logging
        self.debug_responses = True
        
        logger.info("Projection Service (Stage 3) initialized")
        logger.info(f"API configuration | Timeout: {self.api_timeout}s | Max retries: {self.max_retries} | Retry delay: {self.retry_delay}s")
        logger.info(f"API key pool initialized | Count: {len(self.api_key_pool)}")
        logger.info(f"Debug response logging: {'ENABLED' if self.debug_responses else 'DISABLED'}")
    
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
    
    async def process_with_gemini(self, prompt: str, content: str, model: str, api_key: str, operation_name: str = "Projection Engine") -> str:
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
                
                # Create text-based content (Stage 3 works with text analysis)
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
    
    def _extract_methodology_string(self, stage3_result: Dict) -> str:
        """Extract methodology information from stage3 result and return as string"""
        try:
            projection_methodology = stage3_result.get('projection_methodology', {})
            
            if not projection_methodology:
                return "ARIMA (fallback methodology due to limited analysis)"
            
            # Extract key components from projection methodology
            primary_method = projection_methodology.get('primary_method_applied', 'Unknown')
            integration_approach = projection_methodology.get('integration_approach', 'Standard approach')
            
            # Create meaningful string representation
            methodology_str = f"{primary_method}"
            if integration_approach and integration_approach != 'Standard approach':
                methodology_str += f" with {integration_approach}"
            
            logger.debug(f"Extracted methodology string: {methodology_str}")
            return methodology_str
            
        except Exception as e:
            logger.warning(f"Error extracting methodology string: {str(e)}")
            return "Mixed forecasting methodology (analysis incomplete)"

    def _extract_confidence_levels(self, stage3_result: Dict) -> Dict[str, str]:
        """Extract confidence levels from stage3 result and return as dictionary"""
        try:
            confidence_levels = {}
            base_projections = stage3_result.get('base_case_projections', {})
            
            # Extract confidence levels for each projection period
            for period_key, period_data in base_projections.items():
                if isinstance(period_data, dict):
                    # Try to get confidence from revenue data (first available)
                    revenue_data = period_data.get('revenue', [])
                    if revenue_data and isinstance(revenue_data, list) and len(revenue_data) > 0:
                        first_revenue = revenue_data[0]
                        if isinstance(first_revenue, dict):
                            confidence = first_revenue.get('confidence', 'medium')
                            confidence_levels[period_key] = confidence
                        else:
                            confidence_levels[period_key] = 'medium'
                    else:
                        confidence_levels[period_key] = 'medium'
                else:
                    confidence_levels[period_key] = 'medium'
            
            # If no confidence levels found, provide default structure
            if not confidence_levels:
                confidence_levels = {
                    '1_year_ahead': 'medium',
                    '3_years_ahead': 'medium',
                    '5_years_ahead': 'low',
                    '10_years_ahead': 'low',
                    '15_years_ahead': 'very_low'
                }
            
            logger.debug(f"Extracted confidence levels: {confidence_levels}")
            return confidence_levels
            
        except Exception as e:
            logger.warning(f"Error extracting confidence levels: {str(e)}")
            return {
                '1_year_ahead': 'medium',
                '3_years_ahead': 'medium',
                '5_years_ahead': 'low',
                '10_years_ahead': 'low',
                '15_years_ahead': 'very_low'
            }

    def local_validation(self, projections: Dict) -> Dict:
        """Enhanced validation and reconciliation"""
        logger.info(f"🔍 LOCAL VALIDATION: Financial Reconciliation & Consistency Checks")
        
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'reconciliation_checks': [],
            'consistency_scores': {}
        }
        
        try:
            # Check for required projection periods
            required_periods = ['1_year_ahead', '3_years_ahead', '5_years_ahead', '10_years_ahead', '15_years_ahead']
            base_projections = projections.get('base_case_projections', {})
            
            logger.debug(f"🔍 Validating {len(base_projections)} projection periods against {len(required_periods)} required")
            
            for period in required_periods:
                if period not in base_projections:
                    validation_results['warnings'].append(f"Missing projection period: {period}")
                    logger.warning(f"⚠️ Missing projection period: {period}")
                else:
                    period_data = base_projections[period]
                    required_metrics = ['revenue', 'gross_profit', 'expenses', 'net_profit']
                    
                    for metric in required_metrics:
                        if metric not in period_data:
                            validation_results['errors'].append(f"Missing {metric} in {period}")
                            validation_results['valid'] = False
                            logger.error(f"❌ Missing {metric} in {period}")
                        else:
                            metric_data = period_data[metric]
                            if isinstance(metric_data, list) and len(metric_data) > 0:
                                # Financial reconciliation checks
                                if metric == 'net_profit' and 'revenue' in period_data and 'expenses' in period_data:
                                    revenue_data = period_data['revenue']
                                    expenses_data = period_data['expenses']
                                    if len(revenue_data) > 0 and len(expenses_data) > 0:
                                        first_revenue = revenue_data[0].get('value', 0)
                                        first_expenses = expenses_data[0].get('value', 0)
                                        first_net_profit = metric_data[0].get('value', 0)
                                        
                                        # Basic P&L reconciliation check
                                        expected_net = first_revenue - first_expenses
                                        variance = abs(first_net_profit - expected_net) / max(abs(expected_net), 1)
                                        
                                        if variance > 0.1:  # 10% tolerance
                                            validation_results['warnings'].append(f"Net profit reconciliation variance in {period}: {variance:.2%}")
                                            logger.warning(f"⚠️ P&L reconciliation variance in {period}: {variance:.2%}")
                                        
                                        validation_results['reconciliation_checks'].append({
                                            'period': period,
                                            'check': 'net_profit_reconciliation',
                                            'variance': variance,
                                            'status': 'passed' if variance <= 0.1 else 'warning'
                                        })
                                
                                logger.debug(f"✅ Found {metric} in {period} with {len(metric_data)} data points")
            
            # Cross-statement consistency checks
            if base_projections:
                validation_results['consistency_scores']['projection_completeness'] = len(base_projections) / len(required_periods)
                
                # Check for logical consistency across metrics
                total_checks = 0
                passed_checks = 0
                
                for period, data in base_projections.items():
                    if all(metric in data for metric in ['revenue', 'gross_profit', 'expenses']):
                        total_checks += 1
                        # Check if gross profit <= revenue
                        revenue_values = [item.get('value', 0) for item in data.get('revenue', [])]
                        gross_profit_values = [item.get('value', 0) for item in data.get('gross_profit', [])]
                        
                        if revenue_values and gross_profit_values:
                            if all(gp <= rev for gp, rev in zip(gross_profit_values, revenue_values)):
                                passed_checks += 1
                            else:
                                validation_results['warnings'].append(f"Gross profit > Revenue in {period}")
                
                if total_checks > 0:
                    validation_results['consistency_scores']['logical_consistency'] = passed_checks / total_checks
            
            # Overall validation score
            error_weight = len(validation_results['errors']) * 0.5
            warning_weight = len(validation_results['warnings']) * 0.1
            validation_results['overall_score'] = max(0, 1.0 - error_weight - warning_weight)
            
            logger.info(f"✅ Validation Complete: Valid={validation_results['valid']}, Score={validation_results['overall_score']:.2f}, Warnings={len(validation_results['warnings'])}, Errors={len(validation_results['errors'])}")
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {str(e)}")
            validation_results['valid'] = False
            logger.error(f"❌ Validation error: {str(e)}")
        
        return validation_results
    
    async def generate_projections(self, stage2_result: Dict, model: str = "gemini-2.5-pro") -> Dict[str, Any]:
        """
        Stage 3: Integrated projection engine with scenario planning
        
        Args:
            stage2_result: Result from Stage 2 business analysis
            model: Model to use for projections
            
        Returns:
            Dict containing financial projections and scenario planning
        """
        try:
            logger.info(f"🚀 STAGE 3: Projection Engine - Generating Financial Forecasts")
            
            api_key = self.get_next_api_key()
            
            template = string.Template(STAGE3_PROJECTION_PROMPT)
            context_prompt = template.substitute(
                stage2_analysis_output=json.dumps(stage2_result, indent=2)
            )
            
            logger.debug(f"📈 Projection context prepared: {len(context_prompt)} characters")
            
            response = await self.process_with_gemini(
                context_prompt,
                "",
                model,
                api_key,
                "Stage 3: Projection Engine"
            )
            
            # Parse response with multiple strategies
            try:
                if self.debug_responses:
                    logger.info(f"🔍 STAGE 3 - Attempting JSON parsing for projections")
                    logger.info(f"📝 Raw response length: {len(response)} characters")
                    logger.info(f"📋 Raw response preview: {response[:500]}...")
                
                # Strategy 1: Look for JSON in code blocks
                json_blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
                if json_blocks:
                    if self.debug_responses:
                        logger.info(f"✅ Found JSON in code blocks: {len(json_blocks)} blocks")
                    result = json.loads(json_blocks[0])
                    projections_count = len(result.get('base_case_projections', {}))
                    logger.info(f"✅ Stage 3 Success: Generated {projections_count} projection horizons")
                    return result

                # Strategy 2: Look for the first JSON object in the text
                if self.debug_responses:
                    logger.info("⚠️ No JSON code blocks found, searching for raw JSON")
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    if self.debug_responses:
                        logger.info(f"✅ Found raw JSON match: {json_match.group(0)[:200]}...")
                    result = json.loads(json_match.group(0))
                    projections_count = len(result.get('base_case_projections', {}))
                    logger.info(f"✅ Stage 3 Success: Generated {projections_count} projection horizons")
                    return result

                # Strategy 3: Fallback structure
                logger.warning("⚠️ No JSON found in Stage 3 response, using fallback structure")
                return {
                    "projection_methodology": {
                        "primary_method_applied": stage2_result.get('methodology_evaluation', {}).get('selected_method', {}).get('primary_method', 'ARIMA'),
                        "integration_approach": "Fallback projections due to parsing issues"
                    },
                    "base_case_projections": {},
                    "scenario_projections": {"optimistic": {}, "conservative": {}},
                    "assumption_documentation": {"critical_assumptions": []},
                    "executive_summary": "Projection generation completed with fallback structure",
                    "raw_projections": response
                }
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON parsing failed in Stage 3: {str(e)}")
                return {
                    "projection_methodology": {"primary_method_applied": "fallback", "integration_approach": "Error recovery"},
                    "raw_projections": response,
                    "error": str(e)
                }

        except Exception as e:
            logger.error(f"❌ Stage 3 projection generation failed: {str(e)}")
            return {"error": str(e)}
    
    def get_methodology_string(self, stage3_result: Dict) -> str:
        """Get methodology string from Stage 3 result"""
        return self._extract_methodology_string(stage3_result)
    
    def get_confidence_levels(self, stage3_result: Dict) -> Dict[str, str]:
        """Get confidence levels from Stage 3 result"""
        return self._extract_confidence_levels(stage3_result)
    
    def validate_projections(self, projections: Dict) -> Dict:
        """Validate projections for consistency and completeness"""
        return self.local_validation(projections)

# Create projection service instance
projection_service = ProjectionService() 