"""
Enhanced OCR Service - Stage 1: Data Extraction, Normalization, and Quality Assessment
Moved from multi_pdf_service to create separate stage-based services
"""
import asyncio
import time
import json
import re
import base64
from typing import Tuple, Dict, Any
from fastapi import HTTPException

from google import genai
from config import get_next_key, API_KEYS, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY
from models import OCRResponse
from prompts import STAGE1_EXTRACTION_PROMPT
from logging_config import (get_logger, log_api_call, log_file_processing, 
                          log_stage_progress, log_validation_result)

# Set up logger
logger = get_logger(__name__)

class EnhancedOCRService:
    """Enhanced OCR Service for Stage 1: Data extraction, normalization, and quality assessment"""
    
    def __init__(self):
        # File size limits by type
        self.max_pdf_size = 50 * 1024 * 1024   # 50MB for PDFs
        self.max_csv_size = 25 * 1024 * 1024   # 25MB for CSV files
        self.max_image_size = 10 * 1024 * 1024 # 10MB for images
        
        # API configuration from config
        self.api_timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY
        
        # API key pool management
        self.api_key_pool = API_KEYS.copy()
        self.api_key_index = 0
        
        # Debug flag for detailed response logging
        self.debug_responses = True
        
        logger.info("Enhanced OCR Service (Stage 1) initialized")
        logger.info(f"Service configuration | PDF limit: {self.max_pdf_size//1024//1024}MB | CSV limit: {self.max_csv_size//1024//1024}MB | Image limit: {self.max_image_size//1024//1024}MB")
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
    
    async def process_with_gemini(self, prompt: str, content: Any, model: str, api_key: str, operation_name: str = "OCR") -> str:
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
    
    async def process_ocr(self, content: bytes, filename: str, model: str = "gemini-2.5-pro") -> OCRResponse:
        """
        Enhanced OCR processing with Stage 1 logic: Data extraction, normalization, and quality assessment
        """
        try:
            log_stage_progress(logger, "1", f"Processing '{filename}'", "Extract, Normalize, Quality Assessment")
            
            # Validate file
            self.validate_file(filename, content)
            
            # Get file type and MIME type
            file_type, _ = self.get_file_type_and_mime(filename, content)
            api_key = self.get_next_api_key()
            
            # Prepare content for analysis
            if file_type == 'csv':
                csv_text = self.process_csv_content(content, filename)
                content_for_analysis = f"CSV File: {filename}\n\n{csv_text}"
                logger.debug(f"Content preparation | Type: CSV | Length: {len(csv_text)} chars")
            else:
                content_for_analysis = content  # keep binary for PDFs/images
                logger.debug(f"Content preparation | Type: {file_type.upper()} | Size: {len(content)} bytes")
            
            # Process with Gemini using Stage 1 prompt
            response = await self.process_with_gemini(
                STAGE1_EXTRACTION_PROMPT,
                content_for_analysis,
                model,
                api_key,
                f"Stage 1: Extract & Normalize - {filename}"
            )
            
            # Parse JSON response
            try:
                if self.debug_responses:
                    logger.info(f"🔍 STAGE 1 - Attempting JSON parsing for {filename}")
                    logger.info(f"📝 Raw response length: {len(response)} characters")
                    logger.info(f"📋 Raw response preview: {response[:500]}...")
                
                json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_blocks:
                    if self.debug_responses:
                        logger.info(f"✅ Found JSON in code blocks: {len(json_blocks)} blocks")
                    result = json.loads(json_blocks[0])
                    logger.debug("JSON parsing | Source: code block")
                else:
                    if self.debug_responses:
                        logger.info("⚠️ No JSON code blocks found, searching for raw JSON")
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        if self.debug_responses:
                            logger.info(f"✅ Found raw JSON match: {json_match.group(0)[:200]}...")
                        result = json.loads(json_match.group(0))
                        logger.debug("JSON parsing | Source: raw response")
                    else:
                        logger.error("❌ No JSON found in response")
                        raise ValueError("No JSON found in response")
                
                # Extract quality score for logging
                quality_score = result.get('data_quality_assessment', {}).get('completeness_score', 'N/A')
                doc_type = result.get('document_type', 'Unknown')
                log_stage_progress(logger, "1", "SUCCESS", f"File: {filename} | Type: {doc_type} | Quality Score: {quality_score}")
                
                # Return enhanced OCR response with structured data
                return OCRResponse(
                    success=True,
                    data=json.dumps(result, indent=2),  # Return formatted JSON as string for compatibility
                    error=None
                )
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parsing FAILED | File: {filename} | Error: {str(e)}")
                return OCRResponse(
                    success=False,
                    data=response,  # Return raw response for debugging
                    error=f"JSON parsing failed: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Stage 1 FAILED | File: {filename} | Error: {str(e)}")
            return OCRResponse(
                success=False,
                data="",
                error=f"Enhanced OCR processing failed: {str(e)}"
            )

# Create enhanced OCR service instance
ocr_service = EnhancedOCRService() 