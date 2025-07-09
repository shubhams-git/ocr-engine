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
from prompts import OCR_PROMPT

logger = logging.getLogger(__name__)

class OCRService:
    """Service for handling OCR processing with API key rotation"""
    
    def __init__(self):
        # File size limits by type
        self.max_pdf_size = 50 * 1024 * 1024   # 50MB for PDFs
        self.max_csv_size = 25 * 1024 * 1024   # 25MB for CSV files
        self.max_image_size = 10 * 1024 * 1024 # 10MB for images
    
    def get_file_type_and_mime(self, filename: str, content: bytes) -> Tuple[str, str]:
        """Determine file type and MIME type from filename and content"""
        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        filename_lower = filename.lower()
        
        # Check for CSV files
        if filename_lower.endswith('.csv'):
            return 'csv', 'text/csv'
        
        # Check for PDF files
        elif filename_lower.endswith('.pdf'):
            # Validate PDF header
            if not content.startswith(b'%PDF'):
                raise HTTPException(status_code=400, detail="File does not appear to be a valid PDF")
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
            
            return 'image', mime_type
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload an image (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP), PDF, or CSV file."
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
        
        if file_type == 'pdf' and len(content) > self.max_pdf_size:
            raise HTTPException(status_code=413, detail="PDF file too large. Maximum size is 50MB")
        elif file_type == 'csv' and len(content) > self.max_csv_size:
            raise HTTPException(status_code=413, detail="CSV file too large. Maximum size is 25MB")
        elif file_type == 'image' and len(content) > self.max_image_size:
            raise HTTPException(status_code=413, detail="Image file too large. Maximum size is 10MB")
    
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
    
    def process_csv_content(self, content: bytes) -> str:
        """Convert CSV bytes to text with proper encoding detection"""
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                csv_text = content.decode(encoding)
                logger.info(f"Successfully decoded CSV with {encoding} encoding")
                return csv_text
            except UnicodeDecodeError:
                continue
        
        raise HTTPException(
            status_code=400, 
            detail="Unable to decode CSV file. Please ensure it's a valid text file with UTF-8, Latin-1, or Windows-1252 encoding."
        )
    
    async def process_ocr(self, content: bytes, filename: str, model: str = "gemini-2.5-flash") -> OCRResponse:
        """Process OCR with API key rotation"""
        try:
            # Validate file
            self.validate_file(filename, content)
            
            # Get file type and MIME type
            file_type, mime_type = self.get_file_type_and_mime(filename, content)
            
            # Try with each API key until one works
            last_error = None
            
            for attempt in range(len(API_KEYS)):
                try:
                    # Get next API key
                    api_key = get_next_key()
                    current_client = genai.Client(api_key=api_key)
                    
                    logger.info(f"Processing {file_type.upper()} with model {model} (attempt {attempt + 1})")
                    
                    if file_type == 'csv':
                        # For CSV files, send as text prompt
                        csv_text = self.process_csv_content(content)
                        
                        # Create a comprehensive prompt for CSV analysis
                        csv_prompt = f"""
Please analyze and extract the data from this CSV file. Present the data in a clear, structured JSON format that preserves the original structure and relationships.

CSV Content:
{csv_text}

{OCR_PROMPT}
"""
                        
                        # Send as text-only request
                        response = current_client.models.generate_content(
                            model=model,
                            contents=[csv_prompt]
                        )
                    
                    else:
                        # For images and PDFs, send as binary with file content
                        response = current_client.models.generate_content(
                            model=model,
                            contents=[
                                types.Part.from_bytes(
                                    data=content,
                                    mime_type=mime_type,
                                ),
                                OCR_PROMPT
                            ]
                        )
                    
                    # Extract response text
                    extracted_text = self.extract_response_text(response)
                    logger.info(f"{file_type.upper()} processing completed successfully")
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
            logger.error(f"Error processing file: {str(e)}")
            return OCRResponse(success=False, data="", error=str(e))

# Create a single instance to use across the app
ocr_service = OCRService() 