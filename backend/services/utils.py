import json
import json5
import re
import logging
import time
import math
from typing import Optional, Dict, Any

class SuperRobustJSONParser:
    """
    Ultra-robust JSON parser specifically designed to handle Gemini 2.5 Pro responses
    Implements 9 different parsing strategies to handle various response formats
    FIXED: Replaced catastrophic backtracking regex with safe alternative
    ENHANCED: Added projection-specific extraction methods
    """
    
    @staticmethod
    def _extract_projection_data(text: str) -> Optional[Dict[str, Any]]:
        """
        Special extraction method for projection data - handles Stage 4 responses
        """
        logger = logging.getLogger(__name__)
        
        # Look for base_case_projections specifically with safe patterns
        projection_patterns = [
            r'"base_case_projections"\s*:\s*\{',
            r'base_case_projections.*?\{',
            r'\{[^{}]*"base_case_projections"[^{}]*\{'
        ]
        
        for pattern in projection_patterns:
            if re.search(pattern, text, re.DOTALL | re.IGNORECASE):
                logger.debug(f"🔧 Found projection pattern: {pattern}")
                
                # Try to extract the full JSON containing projections using safe scanning
                try:
                    # Find the start of the JSON object
                    start_pos = text.find('{')
                    if start_pos == -1:
                        continue
                    
                    # Use safe brace matching instead of regex
                    brace_count = 0
                    end_pos = -1
                    
                    for i in range(start_pos, len(text)):
                        if text[i] == '{':
                            brace_count += 1
                        elif text[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = i + 1
                                break
                    
                    if end_pos > start_pos:
                        candidate = text[start_pos:end_pos]
                        if 'base_case_projections' in candidate:
                            try:
                                result = json.loads(candidate)
                                if isinstance(result, dict) and 'base_case_projections' in result:
                                    logger.info("✅ Successfully extracted projection data with brace matching")
                                    return result
                            except json.JSONDecodeError:
                                try:
                                    result = json5.loads(candidate)
                                    if isinstance(result, dict) and 'base_case_projections' in result:
                                        logger.info("✅ Successfully extracted projection data with JSON5")
                                        return result
                                except:
                                    continue
                                    
                except Exception as e:
                    logger.debug(f"⚠️ Projection extraction error: {str(e)}")
                    continue
        
        return None

    @staticmethod
    def parse_gemini_response(response_text: str) -> Dict[str, Any]:
        """
        Ultra-robust JSON parser for Gemini responses.
        Tries multiple strategies to find and parse JSON.
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"--- Starting Robust JSON Parsing | Length: {len(response_text)} chars ---")

        # First, try special projection extraction if relevant keywords are present
        if 'base_case_projections' in response_text:
            logger.debug("🔍 'base_case_projections' keyword found, attempting special extraction...")
            projection_data = SuperRobustJSONParser._extract_projection_data(response_text)
            if SuperRobustJSONParser._is_valid_result(projection_data) and projection_data is not None:
                logger.info("✅ Special projection extraction successful.")
                return projection_data

        # Preprocess the text to remove common noise
        processed_text = SuperRobustJSONParser._comprehensive_preprocessing(response_text)
        
        strategies = [
            ('Direct', SuperRobustJSONParser._strategy_direct),
            ('Markdown Fixed', SuperRobustJSONParser._strategy_markdown_fixed),
            ('Boundaries', SuperRobustJSONParser._strategy_boundaries),
            ('JSON5', SuperRobustJSONParser._strategy_json5),
            ('Pattern', SuperRobustJSONParser._strategy_pattern),
            ('Brace Repair', SuperRobustJSONParser._strategy_brace_repair),
            ('Aggressive', SuperRobustJSONParser._strategy_aggressive),
            ('Emergency', SuperRobustJSONParser._strategy_emergency)
        ]

        parsed_json = None
        for name, strategy_func in strategies:
            try:
                logger.debug(f"Trying strategy: {name}")
                # Most strategies benefit from preprocessing
                text_to_use = processed_text
                
                result = strategy_func(text_to_use)
                
                if SuperRobustJSONParser._is_valid_result(result):
                    logger.info(f"✅ Success with strategy: {name}")
                    parsed_json = result
                    break
            except Exception as e:
                logger.debug(f"Strategy {name} failed: {str(e)}")
                continue
        
        if parsed_json:
            key_count = len(parsed_json.keys()) if isinstance(parsed_json, dict) else 0
            logger.debug(f"✅ JSON parsed | Keys: {key_count}")
            return parsed_json
        else:
            logger.error("❌ All JSON parsing strategies failed.")
            # As a last resort, try emergency strategy on the original, unprocessed text
            try:
                logger.debug("Trying emergency strategy on original unprocessed text.")
                emergency_result = SuperRobustJSONParser._strategy_emergency(response_text)
                if SuperRobustJSONParser._is_valid_result(emergency_result) and emergency_result is not None:
                    logger.warning("⚠️ Emergency strategy succeeded on raw text after all else failed.")
                    return emergency_result
            except Exception as e:
                logger.error(f"Emergency strategy on raw text also failed: {e}")

            raise ValueError("Failed to parse JSON response after all strategies")
    
    @staticmethod
    def _validate_projection_data(base_projections: Dict) -> bool:
        """
        Validate that projection data contains all required elements
        """
        logger = logging.getLogger(__name__)
        
        required_horizons = ['1_year_ahead', '3_years_ahead', '5_years_ahead', '10_years_ahead', '15_years_ahead']
        required_metrics = ['revenue', 'expenses', 'gross_profit', 'net_profit']
        
        if not isinstance(base_projections, dict):
            logger.warning("❌ base_projections is not a dictionary")
            return False
        
        for horizon in required_horizons:
            if horizon not in base_projections:
                logger.warning(f"❌ Missing horizon: {horizon}")
                return False
            
            horizon_data = base_projections[horizon]
            if not isinstance(horizon_data, dict):
                logger.warning(f"❌ Invalid horizon data for {horizon}")
                return False
            
            for metric in required_metrics:
                if metric not in horizon_data:
                    logger.warning(f"❌ Missing metric {metric} in {horizon}")
                    return False
                
                metric_data = horizon_data[metric]
                if not isinstance(metric_data, list) or len(metric_data) == 0:
                    logger.warning(f"❌ Empty or invalid metric data {metric} in {horizon}")
                    return False
        
        logger.info("✅ Projection data validation PASSED - all required elements present")
        return True
    
    @staticmethod
    def _comprehensive_preprocessing(text: str) -> str:
        """Enhanced preprocessing to handle common Gemini response formats"""
        # Remove BOM and normalize
        text = text.encode('utf-8').decode('utf-8-sig')
        
        # Remove markdown code blocks (most common issue)
        text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
        
        # Remove common prefixes that Gemini adds
        prefixes = [
            r'^Here\'s the (?:JSON )?(?:response|analysis|result):?\s*',
            r'^Here is the (?:JSON )?(?:response|analysis|result):?\s*',
            r'^The (?:JSON )?(?:response|analysis|result) is:?\s*',
            r'^JSON:?\s*',
            r'^Result:?\s*',
            r'^Response:?\s*',
            r'^Analysis:?\s*',
            r'^Output:?\s*'
        ]
        
        for prefix in prefixes:
            text = re.sub(prefix, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        return text.strip()

    @staticmethod
    def _strategy_direct(text: str) -> Optional[Dict]:
        """Direct JSON parsing"""
        return json.loads(text)

    @staticmethod
    def _strategy_markdown_fixed(text: str) -> Optional[Dict]:
        """
        FIXED: Extract from markdown blocks using safe string operations instead of regex
        This replaces the catastrophic backtracking regex with simple string scanning
        """
        # Look for markdown code block start
        start_markers = ['```json\n', '```json ', '```\n', '``` ']
        end_marker = '```'
        
        start_pos = -1
        used_marker = None
        
        # Find the start marker
        for marker in start_markers:
            pos = text.find(marker)
            if pos != -1 and (start_pos == -1 or pos < start_pos):
                start_pos = pos
                used_marker = marker
        
        if start_pos == -1:
            return None
            
        # Find content start (after the marker)
        if not used_marker:
            return None
        content_start = start_pos + len(used_marker)
        
        # Find the end marker
        end_pos = text.find(end_marker, content_start)
        if end_pos == -1:
            # Try with the content until the end if no closing marker
            candidate = text[content_start:].strip()
        else:
            candidate = text[content_start:end_pos].strip()
        
        # Try to parse the candidate
        if candidate:
            try:
                result = json.loads(candidate)
                if isinstance(result, dict):
                    return result
            except:
                try:
                    result = json5.loads(candidate)
                    if isinstance(result, dict):
                        return result
                except:
                    pass
        
        return None

    @staticmethod
    def _strategy_boundaries(text: str) -> Optional[Dict]:
        """Find JSON by detecting proper boundaries"""
        start = text.find('{')
        if start == -1:
            return None
        
        # Find matching closing brace using safe scanning
        brace_count = 0
        end = -1
        
        for i in range(start, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        if end > start:
            candidate = text[start:end]
            return json.loads(candidate)
        return None

    @staticmethod
    def _strategy_brace_repair(text: str) -> Optional[Dict]:
        """Repair missing braces"""
        text = text.strip()
        
        # Add missing opening brace
        if not text.startswith('{') and '"' in text:
            text = '{' + text
        
        # Add missing closing braces
        if text.startswith('{'):
            open_count = text.count('{')
            close_count = text.count('}')
            missing = open_count - close_count
            if missing > 0:
                text += '}' * missing
        
        return json.loads(text)

    @staticmethod
    def _strategy_pattern(text: str) -> Optional[Dict]:
        """Pattern-based extraction using simple, safe regex"""
        # Use simple, non-backtracking patterns
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple nested JSON (limited depth)
            r'\{.*?\}',  # Basic JSON pattern (non-greedy)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in sorted(matches, key=len, reverse=True):  # Try largest first
                try:
                    result = json.loads(match)
                    if isinstance(result, dict):
                        return result
                except:
                    try:
                        result = json5.loads(match)
                        if isinstance(result, dict):
                            return result
                    except:
                        continue
        return None

    @staticmethod
    def _strategy_aggressive(text: str) -> Optional[Dict]:
        """Aggressive cleanup and repair"""
        # Remove all extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Quote unquoted keys
        text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)
        
        # Fix unquoted string values (be careful not to break numbers/booleans)
        text = re.sub(r':\s*([^",{\[\]}\s][^,}\]]*?)(\s*[,}])', r': "\1"\2', text)
        
        # Remove trailing commas
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        return json.loads(text)

    @staticmethod
    def _strategy_json5(text: str) -> Optional[Dict]:
        """JSON5 parsing for more flexible syntax"""
        result = json5.loads(text)
        if isinstance(result, dict):
            return result
        return None

    @staticmethod
    def _strategy_emergency(text: str) -> Optional[Dict]:
        """
        Emergency extraction - find any valid JSON substring using safe scanning
        FIXED: Replaced regex with simple string scanning to avoid catastrophic backtracking
        """
        # Look for any complete JSON object in the text using simple scanning
        for i in range(len(text)):
            if text[i] == '{':
                # Found potential start, now find matching end
                brace_count = 0
                for j in range(i, len(text)):
                    if text[j] == '{':
                        brace_count += 1
                    elif text[j] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found complete JSON candidate
                            candidate = text[i:j+1]
                            try:
                                result = json.loads(candidate)
                                if isinstance(result, dict) and len(result) > 0:
                                    return result
                            except:
                                continue
                            break
        return None

    @staticmethod
    def _is_valid_result(result) -> bool:
        """Validate that the result is a meaningful dictionary"""
        return (
            result is not None and
            isinstance(result, dict) and
            len(result) > 0 and
            not all(v is None for v in result.values())
        )

class IntelligentMethodologySelector:
    """
    Intelligent methodology selection based on data characteristics
    instead of defaulting to ARIMA
    """
    @staticmethod
    def select_optimal_methodology(data_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select methodology based on actual data characteristics
        Returns a methodology dictionary suitable for use in responses
        """
        # Extract data characteristics with safe defaults
        has_seasonality = data_characteristics.get('seasonality_detected', False)
        
        # Try to infer seasonality from string content if boolean not available
        if not isinstance(has_seasonality, bool):
            seasonality_text = str(data_characteristics).lower()
            has_seasonality = any(term in seasonality_text for term in ['seasonal', 'season', 'quarterly', 'monthly pattern'])
        
        # Extract data points
        data_points = data_characteristics.get('data_points', 0)
        if data_points == 0:
            # Try to infer from other fields
            time_series_data = data_characteristics.get('time_series', [])
            if isinstance(time_series_data, list):
                data_points = len(time_series_data)
            else:
                data_points = 12  # Default assumption for monthly data over a year
        
        # Extract trend and volatility characteristics
        trend_strength = data_characteristics.get('trend_strength', 'unknown')
        if trend_strength == 'unknown':
            # Try to infer from growth patterns
            growth_indicators = str(data_characteristics).lower()
            if any(term in growth_indicators for term in ['growth', 'increasing', 'growing']):
                trend_strength = 'moderate'
            elif any(term in growth_indicators for term in ['declining', 'decreasing']):
                trend_strength = 'negative'
            else:
                trend_strength = 'weak'
        
        volatility = data_characteristics.get('volatility', 'medium')
        
        # Log the characteristics we're working with
        logger = logging.getLogger(__name__)
        logger.info(f"🎯 Methodology Selection - Seasonality: {has_seasonality}, Data Points: {data_points}, Trend: {trend_strength}, Volatility: {volatility}")
        
        # Intelligent selection logic
        if has_seasonality and data_points >= 24:
            # Use Prophet for seasonal data with sufficient history
            return {
                "primary_method": "Prophet",
                "rationale": "Seasonal patterns detected with sufficient data history (24+ points)",
                "confidence_level": "high",
                "fallback_method": "SARIMA",
                "data_requirements": "seasonal_data_sufficient"
            }
        elif data_points >= 36 and trend_strength in ['strong', 'moderate']:
            # Use SARIMA for longer series with trends
            return {
                "primary_method": "SARIMA", 
                "rationale": "Strong trend detected with adequate data history (36+ points)",
                "confidence_level": "high",
                "fallback_method": "Prophet",
                "data_requirements": "long_series_with_trend"
            }
        elif has_seasonality and data_points >= 12:
            # Use seasonal methods even with shorter history
            return {
                "primary_method": "SARIMA",
                "rationale": "Seasonal patterns detected with moderate data history",
                "confidence_level": "medium",
                "fallback_method": "ExponentialSmoothing",
                "data_requirements": "seasonal_moderate_history"
            }
        elif data_points >= 12:
            # Use Exponential Smoothing for medium-term data
            return {
                "primary_method": "ExponentialSmoothing",
                "rationale": "Moderate data history suitable for exponential smoothing",
                "confidence_level": "medium",
                "fallback_method": "LinearRegression",
                "data_requirements": "medium_term_data"
            }
        else:
            # Use Linear Regression for limited data (better than ARIMA for short series)
            return {
                "primary_method": "LinearRegression",
                "rationale": "Limited data history - linear trend projection most appropriate",
                "confidence_level": "low",
                "fallback_method": "MovingAverage",
                "data_requirements": "limited_data_history"
            }
    
    @staticmethod
    def get_methodology_string(methodology_dict: Dict[str, Any]) -> str:
        """
        Convert methodology dictionary to a readable string
        """
        method = methodology_dict.get('primary_method', 'Unknown')
        rationale = methodology_dict.get('rationale', '')
        confidence = methodology_dict.get('confidence_level', 'medium')
        
        return f"{method} (confidence: {confidence}) - {rationale}"

# Utility function for creating intelligent fallback responses
def create_intelligent_fallback_response(stage_result: Dict, parsing_error: str, stage_name: str) -> Dict[str, Any]:
    """
    Create intelligent fallback response instead of defaulting to ARIMA
    """
    logger = logging.getLogger(__name__)
    logger.warning(f"Creating intelligent fallback for {stage_name} due to: {parsing_error}")
    
    # Extract any available data characteristics from the stage result
    business_context = stage_result.get('business_context', {})
    
    # Try to extract seasonality indicators
    seasonality_detected = False
    seasonal_indicators = ['seasonal', 'quarterly', 'monthly']
    content_str = str(stage_result).lower()
    seasonality_detected = any(indicator in content_str for indicator in seasonal_indicators)
    
    # Create data characteristics from available info
    data_characteristics = {
        'seasonality_detected': seasonality_detected,
        'data_points': 24,  # Assume reasonable default for monthly data
        'trend_strength': 'moderate',
        'volatility': 'medium',
        'business_context': business_context
    }
    
    # Use intelligent selection
    methodology = IntelligentMethodologySelector.select_optimal_methodology(data_characteristics)
    
    logger.info(f"✅ Intelligent fallback selected: {methodology['primary_method']} for {stage_name}")
    
    return {
        f"{stage_name.lower()}_processing_summary": {
            "analysis_completed": False,
            "methodology_selection_completed": True,
            "intelligent_fallback_used": True,
            "parsing_error_occurred": True
        },
        "methodology_optimization": {
            "optimal_methodology_selection": methodology
        },
        "intelligent_fallback_used": True,
        "original_parsing_error": parsing_error,
        "fallback_timestamp": str(time.time()),
        "methodology_selection_basis": "intelligent_data_characteristics_analysis"
    }