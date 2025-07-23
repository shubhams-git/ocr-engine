"""
Enhanced OCR Service - Stage 1: Data Extraction with Smart Fallback (Flash Model Only)
Updated to use smart configuration but Flash model doesn't need fallback logic
"""
import asyncio
import time
import json
import json5
import re
import base64
from typing import Tuple, Dict, Any, Optional
from fastapi import HTTPException

from google import genai
from config import (
    get_next_key, API_KEYS, API_TIMEOUT, MAX_RETRIES, BASE_RETRY_DELAY,
    MAX_RETRY_DELAY, EXPONENTIAL_MULTIPLIER, OVERLOAD_MULTIPLIER,
    calculate_smart_backoff_delay
)
from models import OCRResponse
from prompts import STAGE1_EXTRACTION_PROMPT
from logging_config import (get_logger, log_api_call, log_file_processing, 
                          log_stage_progress, log_validation_result)

# Set up logger
logger = get_logger(__name__)

# SIMPLE GLOBAL RATE LIMITER - Flash Model Only
class SimpleGlobalRateLimiter:
    """Simple global rate limiter for Flash model only"""
    
    def __init__(self):
        self.flash_min_delay = 2.5  # 2.5s for Flash model
        self.last_flash_request_time = 0
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

# Create simple global rate limiter instance
simple_global_rate_limiter = SimpleGlobalRateLimiter()

class RobustJSONParser:
    """Robust JSON parser that can handle malformed AI responses"""
    
    @staticmethod
    def clean_and_parse_json(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Robust JSON parser that can handle various AI response formats and common JSON errors
        """
        if not response_text or not isinstance(response_text, str):
            logger.warning("❌ Invalid input: empty or non-string response")
            return None
        
        # Clean the response text
        cleaned_text = response_text.strip()
        
        # Try multiple parsing approaches
        parsing_attempts = [
            ("Direct JSON parsing", lambda x: json.loads(x)),
            ("JSON5 parsing", lambda x: json5.loads(x)),  
            ("Extract from markdown", RobustJSONParser._extract_from_markdown),
            ("Extract JSON patterns", RobustJSONParser._extract_json_patterns),
            ("Repair and parse", RobustJSONParser._repair_and_parse),
        ]
        
        for attempt_name, parse_func in parsing_attempts:
            try:
                logger.debug(f"🔧 Attempting: {attempt_name}")
                result = parse_func(cleaned_text)
                
                if result and isinstance(result, dict):
                    logger.info(f"✅ Successfully parsed with: {attempt_name}")
                    return result
                else:
                    logger.debug(f"⚠️ {attempt_name} returned invalid result: {type(result)}")
                    
            except Exception as e:
                logger.debug(f"❌ {attempt_name} failed: {str(e)}")
                continue
        
        logger.error("❌ All JSON parsing attempts failed")
        return None
    
    @staticmethod
    def _extract_from_markdown(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from markdown code blocks"""
        json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL | re.IGNORECASE)
        
        for block in json_blocks:
            try:
                result = json.loads(block.strip())
                if isinstance(result, dict):
                    return result
            except:
                try:
                    result = json5.loads(block.strip())
                    if isinstance(result, dict):
                        return result
                except:
                    continue
        
        return None
    
    @staticmethod
    def _repair_and_parse(text: str) -> Optional[Dict[str, Any]]:
        """Attempt to repair common JSON formatting issues"""
        repaired = RobustJSONParser._repair_json_format(text)
        if repaired:
            try:
                result = json.loads(repaired)
                if isinstance(result, dict):
                    return result
            except:
                try:
                    result = json5.loads(repaired)
                    if isinstance(result, dict):
                        return result
                except:
                    pass
        return None
    
    @staticmethod
    def _repair_json_format(text: str) -> Optional[str]:
        """Fix common JSON formatting issues"""
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if not json_match:
                return None
            
            content = json_match.group(0)
            
            # Basic repairs
            content = re.sub(r',\s*}', '}', content)  # Remove trailing commas before }
            content = re.sub(r',\s*]', ']', content)  # Remove trailing commas before ]
            content = re.sub(r':\s*,', ': null,', content)  # Replace empty values
            
            return content
            
        except Exception:
            return None
    
    @staticmethod
    def _extract_json_patterns(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON using pattern matching"""
        patterns = [
            r'\{(?:[^{}]|{[^{}]*})*\}',  # Simple nested JSON
            r'\{.*?\}',  # Basic JSON pattern
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
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

class EnhancedOCRService:
    """Enhanced OCR Service for Stage 1: Data extraction with smart backoff (Flash model only)"""
    
    def __init__(self):
        # File size limits by type
        self.max_pdf_size = 50 * 1024 * 1024   # 50MB for PDFs
        self.max_csv_size = 25 * 1024 * 1024   # 25MB for CSV files
        self.max_image_size = 10 * 1024 * 1024 # 10MB for images
        
        # API configuration from enhanced config
        self.api_timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.base_retry_delay = BASE_RETRY_DELAY
        self.max_retry_delay = MAX_RETRY_DELAY
        self.exponential_multiplier = EXPONENTIAL_MULTIPLIER
        self.overload_multiplier = OVERLOAD_MULTIPLIER
        
        # Debug flag for detailed response logging
        self.debug_responses = False  # Disabled for performance
        
        # Only log during main server process, not during uvicorn reloads
        import os
        if os.getenv("OCR_SERVER_MAIN") == "true":
            logger.info("Enhanced OCR Service (Stage 1) initialized with SMART BACKOFF for Flash model")
            logger.info(f"SMART BACKOFF: Max retries: {self.max_retries} | Base delay: {self.base_retry_delay}s | Max delay: {self.max_retry_delay}s")
            logger.info("NOTE: Stage 1 uses Flash model only - no Pro model fallback needed")
        
        logger.debug(f"Service configuration | PDF limit: {self.max_pdf_size//1024//1024}MB | CSV limit: {self.max_csv_size//1024//1024}MB | Image limit: {self.max_image_size//1024//1024}MB")
        logger.debug(f"Enhanced API configuration | Timeout: {self.api_timeout}s | Max retries: {self.max_retries} | Base delay: {self.base_retry_delay}s")
        logger.debug(f"Smart backoff | Max delay: {self.max_retry_delay}s | Multiplier: {self.exponential_multiplier}x | Overload multiplier: {self.overload_multiplier}x")
        logger.debug(f"API key pool available | Count: {len(API_KEYS)}")
    
    def get_file_type_and_mime(self, filename: str, content: bytes) -> Tuple[str, str]:
        """Determine file type and MIME type from filename and content"""
        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        filename_lower = filename.lower()
        
        # Check for CSV files
        if filename_lower.endswith('.csv'):
            logger.debug(f"📄 File type detected: CSV - {filename}")
            return 'csv', 'text/csv'
        
        # Check for PDF files
        elif filename_lower.endswith('.pdf'):
            # Validate PDF header
            if not content.startswith(b'%PDF'):
                raise HTTPException(status_code=400, detail=f"Invalid PDF: {filename}")
            logger.debug(f"📑 File type detected: PDF - {filename}")
            return 'pdf', 'application/pdf'
        
        # Check for image files
        elif any(filename_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']):
            # Determine MIME type based on extension
            if filename_lower.endswith('.png'):
                mime_type = 'image/png'
            elif filename_lower.endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            elif filename_lower.endswith('.gif'):
                mime_type = 'image/gif'
            elif filename_lower.endswith('.bmp'):
                mime_type = 'image/bmp'
            elif filename_lower.endswith('.tiff'):
                mime_type = 'image/tiff'
            elif filename_lower.endswith('.webp'):
                mime_type = 'image/webp'
            else:
                mime_type = 'image/jpeg'  # Default fallback
            
            logger.debug(f"🖼️ File type detected: Image - {filename} ({mime_type})")
            return 'image', mime_type
        
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {filename}. Use PDF, CSV, or image files (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP)."
            )
    
    def validate_file(self, filename: str, content: bytes) -> None:
        """Validate uploaded file"""
        if not filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check if file has actual content
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Get file type and validate size limits
        file_type, _ = self.get_file_type_and_mime(filename, content)
        file_size_mb = len(content) / 1024 / 1024
        
        if file_type == 'pdf' and len(content) > self.max_pdf_size:
            raise HTTPException(status_code=413, detail=f"PDF {filename} too large (max 50MB)")
        elif file_type == 'csv' and len(content) > self.max_csv_size:
            raise HTTPException(status_code=413, detail=f"CSV {filename} too large (max 25MB)")
        elif file_type == 'image' and len(content) > self.max_image_size:
            raise HTTPException(status_code=413, detail=f"Image {filename} too large (max 10MB)")
        
        logger.info(f"✅ File validated: {filename} ({file_type.upper()}, {file_size_mb:.2f}MB)")
    
    def process_csv_content(self, content: bytes, filename: str) -> str:
        """Convert CSV bytes to text with encoding detection"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                csv_text = content.decode(encoding)
                logger.debug(f"✅ Decoded CSV {filename} with {encoding} encoding")
                return csv_text
            except UnicodeDecodeError:
                continue
        
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot decode CSV {filename}. Use UTF-8 encoding."
        )
    
    def detect_document_type_fallback(self, filename: str, csv_content: str) -> str:
        """Fallback method to detect document type from filename and CSV content"""
        filename_lower = filename.lower()
        content_lower = csv_content.lower()
        
        # Check filename first
        if any(term in filename_lower for term in ['profit', 'loss', 'p&l', 'pl', 'income']):
            logger.info(f"Document type detected from filename: Profit and Loss ({filename})")
            return "Profit and Loss"
        elif any(term in filename_lower for term in ['balance', 'sheet', 'bs']):
            logger.info(f"Document type detected from filename: Balance Sheet ({filename})")
            return "Balance Sheet"
        elif any(term in filename_lower for term in ['cash', 'flow', 'cf']):
            logger.info(f"Document type detected from filename: Cash Flow ({filename})")
            return "Cash Flow"
        
        # Check content structure (first few lines)
        content_lines = csv_content.split('\n')[:10]  # First 10 lines
        content_sample = ' '.join(content_lines).lower()
        
        # Look for P&L indicators
        pl_indicators = ['revenue', 'sales', 'gross profit', 'expenses', 'net profit', 'net income', 'ebitda']
        if any(indicator in content_sample for indicator in pl_indicators):
            logger.info(f"Document type detected from content: Profit and Loss ({filename})")
            return "Profit and Loss"
        
        # Look for Balance Sheet indicators
        bs_indicators = ['assets', 'liabilities', 'equity', 'current assets', 'fixed assets', 'accounts payable']
        if any(indicator in content_sample for indicator in bs_indicators):
            logger.info(f"Document type detected from content: Balance Sheet ({filename})")
            return "Balance Sheet"
        
        # Look for Cash Flow indicators
        cf_indicators = ['operating activities', 'investing activities', 'financing activities', 'cash flow']
        if any(indicator in content_sample for indicator in cf_indicators):
            logger.info(f"Document type detected from content: Cash Flow ({filename})")
            return "Cash Flow"
        
        logger.warning(f"Could not detect document type for {filename}, defaulting to Other")
        return "Other"
    
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
    
    async def process_with_gemini_smart_backoff(self, prompt: str, content: Any, model: str, operation_name: str = "OCR") -> str:
        """Process request with Gemini using SMART BACKOFF for Flash model"""
        start_time = time.time()
        last_exception = None
        had_previous_error = False
        
        # Flash model typically has better quotas
        is_flash_model = "flash" in model.lower()
        
        for attempt in range(self.max_retries + 1):
            try:
                # SIMPLE RATE LIMITING FOR FLASH MODEL
                await simple_global_rate_limiter.acquire_flash(f"{operation_name} (Attempt {attempt + 1})")
                
                # GET FRESH API KEY FOR EACH ATTEMPT
                api_key = get_next_key()
                key_suffix = api_key[-4:] if len(api_key) > 4 else "****"
                
                if attempt == 0:
                    log_api_call(logger, operation_name, model, key_suffix, success=True)
                else:
                    logger.info(f"🔄 API call RETRY {attempt}/{self.max_retries}: {operation_name} | Model: {model} | Key: ...{key_suffix}")
                
                # Use new SDK client with fresh key
                client = genai.Client(api_key=api_key)
                
                if content == "":
                    # Text-only request
                    contents = prompt
                    logger.debug(f"Request type: text-only | Prompt length: {len(prompt)} chars")
                elif isinstance(content, str):
                    # Text + prompt request
                    contents = f"{content}\n\n{prompt}"
                    logger.debug(f"Request type: text + prompt | Content: {len(content)} chars | Prompt: {len(prompt)} chars")
                elif isinstance(content, bytes):
                    # Binary content (PDF) - create multipart content
                    contents = [
                        {"inline_data": {"mime_type": "application/pdf", "data": base64.b64encode(content).decode('utf-8')}},
                        {"text": prompt}
                    ]
                    logger.debug(f"Request type: binary + prompt | Content: {len(content)} bytes | Prompt: {len(prompt)} chars")
                else:
                    # Custom content type
                    contents = f"{str(content)}\n\n{prompt}"
                    logger.debug(f"Request type: custom + prompt | Prompt: {len(prompt)} chars")
                
                # Apply timeout to the API call
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
                
                # Log success
                log_api_call(logger, operation_name, model, key_suffix, elapsed_time, success=True)
                logger.info(f"✅ {operation_name} SUCCESS after {attempt + 1} attempts in {elapsed_time:.2f}s")
                return response_text
                
            except asyncio.TimeoutError as e:
                elapsed_time = time.time() - start_time
                last_exception = e
                had_previous_error = True
                logger.warning(f"⏰ API call TIMEOUT: {operation_name} | Attempt {attempt + 1}/{self.max_retries + 1} | Duration: {elapsed_time:.2f}s")
                
                if attempt >= self.max_retries:
                    break
                    
                # Smart backoff for timeout
                delay = calculate_smart_backoff_delay(attempt, self.base_retry_delay, is_overload=False, had_previous_error=True)
                logger.info(f"⏳ Timeout retry delay: {delay:.1f}s")
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
                
                is_retryable = is_503_overload or other_retryable
                
                if is_retryable and attempt < self.max_retries:
                    if is_503_overload:
                        # Smart backoff with overload handling
                        delay = calculate_smart_backoff_delay(attempt, self.base_retry_delay, is_overload=True, had_previous_error=True)
                        logger.warning(f"🚨 503 OVERLOAD detected - using smart backoff: {delay:.1f}s")
                        logger.warning(f"🔄 Overload retry {attempt + 1}/{self.max_retries}: {operation_name} | Model: {model} | Error: {error_str[:100]}...")
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
        log_api_call(logger, operation_name, model, "FAILED", elapsed_time, success=False, error=final_error)
        logger.error(f"❌ {operation_name} FAILED after {self.max_retries + 1} attempts in {elapsed_time:.2f}s")
        raise last_exception or Exception(f"All {self.max_retries + 1} retry attempts failed")
    
    async def process_ocr(self, content: bytes, filename: str, model: str = "gemini-2.5-flash") -> OCRResponse:
        """
        Enhanced OCR processing with Stage 1 logic and SMART BACKOFF (Flash model only)
        """
        try:
            log_stage_progress(logger, "1", f"Processing '{filename}'", "Extract, Normalize, Quality Assessment with SMART BACKOFF")
            
            # Validate file
            self.validate_file(filename, content)
            
            # Get file type and MIME type
            file_type, _ = self.get_file_type_and_mime(filename, content)
            
            # Prepare content for analysis
            if file_type == 'csv':
                csv_text = self.process_csv_content(content, filename)
                content_for_analysis = f"CSV File: {filename}\n\n{csv_text}"
                logger.debug(f"Content preparation | Type: CSV | Length: {len(csv_text)} chars")
            else:
                content_for_analysis = content  # keep binary for PDFs/images
                logger.debug(f"Content preparation | Type: {file_type.upper()} | Size: {len(content)} bytes")
            
            # Process with Gemini using SMART BACKOFF (Flash only, no fallback needed)
            response = await self.process_with_gemini_smart_backoff(
                STAGE1_EXTRACTION_PROMPT,
                content_for_analysis,
                model,
                f"Stage 1: Enhanced Extract & Normalize - {filename}"
            )
            
            # Parse JSON response using robust parser
            try:
                if self.debug_responses:
                    logger.info(f"🔍 STAGE 1 - Attempting robust JSON parsing for {filename}")
                    logger.info(f"📝 Raw response length: {len(response)} characters")
                    logger.info(f"📋 Raw response preview: {response[:500]}...")
                
                result = RobustJSONParser.clean_and_parse_json(response)
                
                if result and isinstance(result, dict):
                    # Validate and correct document type and filename if needed
                    original_doc_type = result.get('document_type', 'Other')
                    original_filename = result.get('source_filename', 'Unknown')
                    
                    # If Gemini failed to detect the document type correctly, use fallback detection
                    if original_doc_type == 'Other' or original_doc_type == 'Unknown' or not original_doc_type:
                        if file_type == 'csv':
                            corrected_doc_type = self.detect_document_type_fallback(filename, csv_text)
                            if corrected_doc_type != 'Other':
                                result['document_type'] = corrected_doc_type
                                logger.info(f"🔧 Corrected document type from '{original_doc_type}' to '{corrected_doc_type}' for {filename}")
                    
                    # If Gemini failed to detect the filename correctly, use the actual filename
                    if original_filename == 'Unknown' or not original_filename:
                        result['source_filename'] = filename
                        logger.info(f"🔧 Corrected source filename from '{original_filename}' to '{filename}'")
                    
                    # Extract quality score for logging
                    quality_score = result.get('data_quality_assessment', {}).get('completeness_score', 'N/A')
                    doc_type = result.get('document_type', 'Unknown')
                    log_stage_progress(logger, "1", "SUCCESS", f"File: {filename} | Type: {doc_type} | Quality Score: {quality_score}")
                    
                    # Return enhanced OCR response with structured data
                    return OCRResponse(
                        success=True,
                        data=json.dumps(result, indent=2),
                        error=None
                    )
                else:
                    logger.warning(f"⚠️ RobustJSONParser returned invalid result for {filename}: {type(result)}")
                    logger.warning("⚠️ Using enhanced fallback structure")
                    
            except Exception as parse_error:
                logger.error(f"❌ Exception in robust JSON parsing for {filename}: {str(parse_error)}")
                import traceback
                logger.error(f"❌ Parse error traceback: {traceback.format_exc()}")
            
            # Enhanced fallback with original response preserved
            logger.warning(f"🔄 Generating enhanced fallback structure for {filename}")
            
            # Use the comprehensive document type detection method
            if file_type == 'csv':
                doc_type = self.detect_document_type_fallback(filename, csv_text)
            else:
                # For non-CSV files, fall back to basic filename detection
                filename_lower = filename.lower()
                if 'profit' in filename_lower and 'loss' in filename_lower:
                    doc_type = 'Profit and Loss'
                    logger.info(f"📊 Detected P&L document from filename: {filename}")
                elif 'balance' in filename_lower and 'sheet' in filename_lower:
                    doc_type = 'Balance Sheet'
                    logger.info(f"📊 Detected Balance Sheet document from filename: {filename}")
                elif 'cash' in filename_lower and 'flow' in filename_lower:
                    doc_type = 'Cash Flow'
                    logger.info(f"📊 Detected Cash Flow document from filename: {filename}")
                else:
                    doc_type = 'Other'
                    logger.info(f"📊 Unknown document type for: {filename}")
            
            fallback_result = {
                "document_type": doc_type,
                "source_filename": filename,
                "data_quality_assessment": {
                    "completeness_score": 0.5,
                    "total_periods": 1,
                    "period_range": "Unknown",
                    "data_gaps": [],
                    "anomalies_detected": [],
                    "consistency_issues": ["JSON parsing failed - using fallback with smart backoff"],
                    "quality_flags": ["insufficient_data"],
                    "standard_field_coverage": {
                        "total_standard_fields_found": "0 out of 25",
                        "missing_standard_fields": [],
                        "coverage_percentage": "0%"
                    }
                },
                "standard_field_mapping": {
                    "profit_and_loss_standards": {},
                    "balance_sheet_standards": {
                        "assets": {},
                        "liabilities": {},
                        "equity": {}
                    }
                },
                "legacy_normalized_time_series": {
                    "revenue": [],
                    "gross_profit": [],
                    "expenses": [],
                    "net_profit": [],
                    "assets": [],
                    "liabilities": [],
                    "equity": [],
                    "cash_flow": []
                },
                "basic_context": {
                    "currency_detected": "AUD",
                    "business_indicators": ["Fallback structure due to parsing failure with smart backoff"],
                    "reporting_frequency": "monthly",
                    "latest_period": "Unknown"
                },
                "processing_notes": f"JSON parsing failed for {filename}. Using fallback structure with smart backoff support. Raw response preserved.",
                "raw_response": response,
                "parsing_error": "Robust JSON parsing failed - using enhanced fallback structure with smart backoff",
                "smart_backoff_used": True
            }
            
            log_stage_progress(logger, "1", "FALLBACK", f"File: {filename} | Type: {doc_type} | Quality Score: 0.5 (Fallback with smart backoff)")
            
            return OCRResponse(
                success=True,  # Mark as success so document type detection works
                data=json.dumps(fallback_result, indent=2),
                error=None
            )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Stage 1 FAILED | File: {filename} | Error: {str(e)}")
            return OCRResponse(
                success=False,
                data="",
                error=f"Enhanced OCR processing with smart backoff failed: {str(e)}"
            )

# Create enhanced OCR service instance
ocr_service = EnhancedOCRService()