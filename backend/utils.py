"""
Utility functions for OCR Engine
Contains JSON parsing utilities and data normalization functions
"""
import json
import logging
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class DataStructureParser:
    """
    Robust parser for handling nested data structures from OCR responses
    Specifically handles the data.data field structure from Stage 1 results
    """
    
    @staticmethod
    def parse_stage1_data(stage1_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Stage 1 result data, handling the nested data.data structure
        
        Args:
            stage1_result: Stage 1 result dictionary with potential data.data structure
            
        Returns:
            Parsed data dictionary or None if parsing fails
        """
        try:
            logger.debug(f"🔧 Parsing Stage 1 data structure | Keys: {list(stage1_result.keys())}")
            
            # Handle different possible structures
            data_to_parse = None
            
            # Case 1: data.data structure (most common from admin tests)
            if "data" in stage1_result and isinstance(stage1_result["data"], dict):
                data_section = stage1_result["data"]
                if "data" in data_section:
                    data_to_parse = data_section["data"]
                    logger.debug("📋 Found data.data structure")
                else:
                    # data object directly contains the info
                    data_to_parse = data_section
                    logger.debug("📋 Found direct data structure")
            
            # Case 2: Direct data field
            elif "data" in stage1_result:
                data_to_parse = stage1_result["data"]
                logger.debug("📋 Found simple data structure")
            
            # Case 3: No data field found
            else:
                logger.warning("❌ No data field found in Stage 1 result")
                return None
            
            # Parse the data if it's a JSON string
            if isinstance(data_to_parse, str):
                try:
                    parsed_data = json.loads(data_to_parse)
                    logger.debug(f"✅ Successfully parsed JSON string | Keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
                    return parsed_data
                except json.JSONDecodeError as e:
                    logger.warning(f"❌ Failed to parse JSON string: {str(e)}")
                    logger.debug(f"❌ Raw data preview: {data_to_parse[:200]}...")
                    
                    # Try to fix common JSON issues
                    try:
                        # Attempt to fix malformed JSON by finding the last complete object
                        import re
                        
                        # Find all complete JSON objects
                        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                        matches = re.findall(json_pattern, data_to_parse)
                        
                        if matches:
                            # Try parsing the largest match
                            largest_match = max(matches, key=len)
                            fallback_data = json.loads(largest_match)
                            logger.info(f"✅ Recovered partial JSON data using fallback parsing")
                            return fallback_data
                        else:
                            logger.warning(f"❌ No recoverable JSON patterns found")
                            return None
                            
                    except Exception as fallback_error:
                        logger.error(f"❌ Fallback JSON parsing also failed: {str(fallback_error)}")
                        return None
            
            # Data is already a dictionary
            elif isinstance(data_to_parse, dict):
                logger.debug(f"✅ Data already parsed | Keys: {list(data_to_parse.keys())}")
                return data_to_parse
            
            # Unexpected data type
            else:
                logger.warning(f"❌ Unexpected data type: {type(data_to_parse)}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Stage 1 data parsing failed: {str(e)}")
            return None
    
    @staticmethod
    def normalize_stage1_result(stage1_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Stage 1 result to ensure consistent structure for downstream processing
        
        Args:
            stage1_result: Raw Stage 1 result
            
        Returns:
            Normalized result with parsed data
        """
        try:
            # Extract filename
            filename = (
                stage1_result.get("filename") or 
                stage1_result.get("file_info", {}).get("filename") or 
                stage1_result.get("file_info", {}).get("name") or
                "unknown_file"
            )
            
            # Extract success status
            success = stage1_result.get("success", False)
            
            # Parse the data
            parsed_data = DataStructureParser.parse_stage1_data(stage1_result)
            
            # If parsing failed but we have a success flag, check if we have raw_text
            if not parsed_data and success:
                raw_text = stage1_result.get("raw_text")
                if raw_text:
                    logger.warning(f"📝 Data parsing failed but raw_text available for {filename}")
                
            normalized_result = {
                "filename": filename,
                "success": success and parsed_data is not None,
                "data": parsed_data or {},
                "raw_text": stage1_result.get("raw_text"),
                "original_structure": stage1_result  # Keep original for debugging
            }
            
            logger.debug(f"✅ Normalized Stage 1 result | File: {filename} | Success: {normalized_result['success']}")
            return normalized_result
            
        except Exception as e:
            logger.error(f"❌ Stage 1 normalization failed: {str(e)}")
            return {
                "filename": "error_file",
                "success": False,
                "data": {},
                "raw_text": None,
                "error": str(e)
            }

class JSONValidator:
    """Utility class for validating JSON structures"""
    
    @staticmethod
    def validate_financial_data(data: Dict[str, Any]) -> bool:
        """
        Validate that the parsed data contains expected financial structure with flexible field matching
        
        Args:
            data: Parsed financial data
            
        Returns:
            True if structure is valid, False otherwise
        """
        try:
            required_fields = ["document_type", "periods"]
            
            # Check for required top-level fields (relaxed requirements)
            for field in required_fields:
                if field not in data:
                    logger.warning(f"❌ Missing required field: {field}")
                    return False
            
            # Validate periods structure
            periods = data.get("periods", [])
            if not isinstance(periods, list) or len(periods) == 0:
                logger.warning("❌ Periods must be a non-empty list")
                return False
            
            # Check first period has some financial data with flexible field matching
            first_period = periods[0]
            
            # Define flexible field mappings for different document types
            pnl_fields = [
                "revenue", "net_income", "net_profit", "gross_profit", "opex", 
                "operating_expenses", "total_expenses", "ebitda", "earnings_before_tax"
            ]
            bs_fields = [
                "cash", "total_assets", "total_liabilities", "equity", "current_assets", 
                "fixed_assets", "ar", "ap", "inventory", "total_liabilities_equity"
            ]
            cf_fields = [
                "ocf", "icf", "fcf", "operating_cash_flow", "investing_cash_flow", 
                "financing_cash_flow", "capex", "delta_cash"
            ]
            
            # Combine all possible financial fields
            all_financial_fields = pnl_fields + bs_fields + cf_fields
            
            # Check if first period contains any recognizable financial data
            period_keys = set(first_period.keys())
            financial_field_matches = period_keys.intersection(set(all_financial_fields))
            
            # Also check for nested structures (like opex.total)
            nested_financial_data = False
            for key, value in first_period.items():
                if isinstance(value, dict):
                    nested_keys = set(value.keys())
                    if nested_keys.intersection(set(["total", "breakdown"])):
                        nested_financial_data = True
                        break
            
            has_financial_data = len(financial_field_matches) > 0 or nested_financial_data
            
            if not has_financial_data:
                logger.warning(f"❌ No recognizable financial data in periods | Available keys: {list(period_keys)} | Expected any of: {all_financial_fields[:10]}...")
                return False
            
            logger.debug(f"✅ Financial data structure validation passed | Matched fields: {financial_field_matches}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Financial data validation failed: {str(e)}")
            return False
