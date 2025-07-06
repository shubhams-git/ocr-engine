"""
OCR processing service using Google Gemini AI
"""
import logging
from typing import Tuple
from fastapi import HTTPException

from google import genai
from google.genai import types
from config import get_next_key, API_KEYS
from models import OCRResponse

logger = logging.getLogger(__name__)

class OCRService:
    """Service for handling OCR processing with API key rotation"""
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB
    
    def validate_file(self, filename: str, content: bytes) -> None:
        """Validate uploaded file"""
        if not filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if len(content) > self.max_file_size:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
        
        # Basic file type validation
        if not filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Check if file has actual content
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Basic PDF header check
        if not content.startswith(b'%PDF'):
            raise HTTPException(status_code=400, detail="File does not appear to be a valid PDF")
    
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
        
        raise Exception("No data could be extracted from response")
    
    async def process_ocr(self, content: bytes, filename: str, model: str = "gemini-2.5-flash") -> OCRResponse:
        """Process OCR with API key rotation"""
        try:
            # Validate file
            self.validate_file(filename, content)
            
            # Simple prompt for JSON extraction
            prompt = "Extract the accurate data in a json"
            
            # Try with each API key until one works
            last_error = None
            
            for attempt in range(len(API_KEYS)):
                try:
                    # Get next API key
                    api_key = get_next_key()
                    current_client = genai.Client(api_key=api_key)
                    
                    logger.info(f"Processing OCR with model {model} (attempt {attempt + 1})")
                    
                    # Send to Gemini with selected model
                    response = current_client.models.generate_content(
                        model=model,
                        contents=[
                            types.Part.from_bytes(
                                data=content,
                                mime_type='application/pdf',
                            ),
                            prompt
                        ]
                    )
                    
                    # Extract response text
                    extracted_text = self.extract_response_text(response)
                    logger.info("OCR processing completed successfully")
                    return OCRResponse(success=True, data=extracted_text, error=None)
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"API key {attempt + 1} failed: {str(e)}")
            
            # All API keys failed
            logger.error(f"All {len(API_KEYS)} API keys failed. Last error: {str(last_error)}")
            return OCRResponse(success=False, data="", error=f"All API keys failed: {str(last_error)}")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing OCR: {str(e)}")
            return OCRResponse(success=False, data="", error=str(e))

# Create a single instance to use across the app
ocr_service = OCRService() 