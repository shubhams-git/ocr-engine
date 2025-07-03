"""
Gemini AI service for OCR processing with API key rotation
"""
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from PIL import Image
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from ..config import api_manager, GEMINI_MODELS
from ..models import OCRMetadata

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        self.current_api_key = None
        self.current_key_name = ""
        self.model_cache = {}
        self.retry_count = 3
        self.retry_delay = 1  # seconds
        
        # Safety settings for content generation
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        logger.info("🤖 Gemini service initialized")
    
    def _get_api_key(self) -> Dict[str, str]:
        """Get next API key from rotation"""
        key_info = api_manager.get_next_api_key()
        self.current_api_key = key_info['key']
        self.current_key_name = key_info['name']
        
        # Configure the API with new key
        genai.configure(api_key=self.current_api_key)
        logger.info(f"🔑 Configured Gemini with API key: {self.current_key_name}")
        
        return key_info
    
    def _get_model(self, model_name: str):
        """Get or create Gemini model instance"""
        cache_key = f"{self.current_key_name}_{model_name}"
        
        if cache_key not in self.model_cache:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    safety_settings=self.safety_settings
                )
                self.model_cache[cache_key] = model
                logger.info(f"🤖 Created model instance: {model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create model {model_name}: {str(e)}")
                raise
        
        return self.model_cache[cache_key]
    
    async def _make_api_call(self, model, prompt: str, images: List[Image.Image]) -> str:
        """Make API call with retry logic"""
        last_exception = None
        
        for attempt in range(self.retry_count):
            try:
                logger.info(f"🔄 API call attempt {attempt + 1}/{self.retry_count}")
                
                # Prepare content for Gemini
                content = [prompt] + images
                
                # Make the API call
                start_time = time.time()
                response = await asyncio.to_thread(model.generate_content, content)
                end_time = time.time()
                
                # Check if response is valid
                if response and response.text:
                    api_manager.mark_key_success(self.current_key_name)
                    
                    duration_ms = int((end_time - start_time) * 1000)
                    logger.info(f"✅ API call successful in {duration_ms}ms")
                    
                    return response.text.strip()
                else:
                    raise Exception("Empty response from Gemini API")
                    
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # Check for specific error types
                if "quota" in error_msg or "rate" in error_msg:
                    logger.warning(f"⚠️ Rate limit/quota issue: {str(e)}")
                    api_manager.mark_key_failed(self.current_key_name)
                    
                    # Try next API key
                    if attempt < self.retry_count - 1:
                        logger.info("🔄 Switching to next API key")
                        self._get_api_key()
                        model = self._get_model(model.model_name)
                        await asyncio.sleep(self.retry_delay)
                        continue
                        
                elif "safety" in error_msg:
                    logger.error(f"🚫 Content safety issue: {str(e)}")
                    break  # Don't retry safety issues
                    
                else:
                    logger.error(f"❌ API call failed: {str(e)}")
                    if attempt < self.retry_count - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        # If we get here, all attempts failed
        logger.error(f"💥 All API call attempts failed. Last error: {str(last_exception)}")
        raise Exception(f"Gemini API call failed after {self.retry_count} attempts: {str(last_exception)}")
    
    async def extract_text_from_image(
        self, 
        image: Image.Image, 
        model_name: str = "gemini-2.5-flash",
        language: str = "en",
        filename: str = "image"
    ) -> Dict[str, Any]:
        """Extract text from a single image"""
        try:
            logger.info(f"🖼️ Starting OCR for image: {filename}")
            
            # Get API key and model
            self._get_api_key()
            model = self._get_model(model_name)
            
            # Create prompt based on language
            if language == "en":
                prompt = """
                Extract all text from this image with high accuracy. 
                Preserve the original formatting, structure, and layout as much as possible.
                Include all visible text including headers, body text, captions, labels, and any other textual content.
                If there are tables, maintain the table structure.
                If there are multiple columns, preserve the column layout.
                Return only the extracted text without any additional commentary.
                """
            else:
                prompt = f"""
                Extract all text from this image with high accuracy. The text is expected to be in {language} language.
                Preserve the original formatting, structure, and layout as much as possible.
                Include all visible text including headers, body text, captions, labels, and any other textual content.
                If there are tables, maintain the table structure.
                If there are multiple columns, preserve the column layout.
                Return only the extracted text without any additional commentary.
                """
            
            # Make API call
            start_time = time.time()
            extracted_text = await self._make_api_call(model, prompt, [image])
            end_time = time.time()
            
            processing_time_ms = int((end_time - start_time) * 1000)
            
            # Calculate statistics
            word_count = len(extracted_text.split()) if extracted_text else 0
            char_count = len(extracted_text) if extracted_text else 0
            
            logger.info(f"✅ OCR completed: {word_count} words, {char_count} characters")
            
            return {
                "text": extracted_text,
                "confidence": 0.95,  # Gemini doesn't provide confidence scores
                "processing_time_ms": processing_time_ms,
                "word_count": word_count,
                "char_count": char_count,
                "api_key_used": self.current_key_name,
                "model_used": model_name
            }
            
        except Exception as e:
            logger.error(f"💥 OCR failed for {filename}: {str(e)}")
            raise
    
    async def extract_text_from_pdf_pages(
        self, 
        images: List[Image.Image], 
        model_name: str = "gemini-2.5-flash",
        language: str = "en",
        filename: str = "document.pdf"
    ) -> Dict[str, Any]:
        """Extract text from multiple PDF pages"""
        try:
            logger.info(f"📄 Starting OCR for PDF: {filename} ({len(images)} pages)")
            
            all_text = []
            total_processing_time = 0
            page_results = []
            
            for i, image in enumerate(images):
                page_num = i + 1
                logger.info(f"📄 Processing page {page_num}/{len(images)}")
                
                try:
                    result = await self.extract_text_from_image(
                        image, 
                        model_name, 
                        language, 
                        f"{filename}_page_{page_num}"
                    )
                    
                    page_text = result["text"]
                    if page_text.strip():
                        all_text.append(f"--- Page {page_num} ---\n{page_text}")
                        page_results.append({
                            "page": page_num,
                            "text": page_text,
                            "words": result["word_count"],
                            "characters": result["char_count"]
                        })
                    
                    total_processing_time += result["processing_time_ms"]
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process page {page_num}: {str(e)}")
                    all_text.append(f"--- Page {page_num} ---\n[Error processing page: {str(e)}]")
            
            # Combine all text
            combined_text = "\n\n".join(all_text)
            total_words = sum(page["words"] for page in page_results)
            total_chars = sum(page["characters"] for page in page_results)
            
            logger.info(f"✅ PDF OCR completed: {len(page_results)} pages, {total_words} words")
            
            return {
                "text": combined_text,
                "confidence": 0.95,
                "processing_time_ms": total_processing_time,
                "word_count": total_words,
                "char_count": total_chars,
                "pages_processed": len(page_results),
                "page_results": page_results,
                "api_key_used": self.current_key_name,
                "model_used": model_name
            }
            
        except Exception as e:
            logger.error(f"💥 PDF OCR failed for {filename}: {str(e)}")
            raise
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available Gemini models"""
        return GEMINI_MODELS
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        key_stats = api_manager.get_key_stats()
        
        return {
            "service": "Gemini OCR Service",
            "api_keys": key_stats,
            "cached_models": len(self.model_cache),
            "current_key": self.current_key_name,
            "retry_settings": {
                "max_retries": self.retry_count,
                "retry_delay": self.retry_delay
            }
        }

# Global service instance
gemini_service = GeminiService() 