"""
Main OCR service that coordinates file processing and AI calls
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException

from .gemini_service import gemini_service
from ..utils.file_utils import FileValidator, ImageProcessor, PDFProcessor, format_file_size
from ..config import settings
from ..models import OCRResponse, OCRMetadata

logger = logging.getLogger(__name__)

class OCRService:
    """Main service for OCR processing"""
    
    def __init__(self):
        self.supported_image_types = [
            "image/png", "image/jpeg", "image/jpg", "image/gif", 
            "image/bmp", "image/tiff", "image/webp"
        ]
        self.supported_document_types = ["application/pdf"]
        self.file_validator = FileValidator()
        self.image_processor = ImageProcessor()
        self.pdf_processor = PDFProcessor()
        
        logger.info("🔧 OCR service initialized")
    
    async def process_file(
        self, 
        file: UploadFile, 
        model: str = "gemini-2.5-flash",
        language: str = "en"
    ) -> OCRResponse:
        """Process uploaded file for OCR"""
        try:
            start_time = time.time()
            logger.info(f"📝 Processing file: {file.filename} (model: {model}, language: {language})")
            
            # Validate file
            await self._validate_file(file)
            
            # Get file info
            file_info = await self.file_validator.get_file_info(file)
            logger.info(f"📁 File info: {file_info}")
            
            # Process based on file type
            if file_info["actual_mime_type"] in self.supported_image_types:
                result = await self._process_image(file, model, language, file_info)
            elif file_info["actual_mime_type"] in self.supported_document_types:
                result = await self._process_pdf(file, model, language, file_info)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file_info['actual_mime_type']}"
                )
            
            # Create metadata
            metadata = self._create_metadata(file_info, result, model, language)
            
            # Create response
            total_time = time.time() - start_time
            response = OCRResponse(
                text=result["text"],
                confidence=result["confidence"],
                metadata=metadata,
                processing_time_ms=int(total_time * 1000)
            )
            
            logger.info(f"✅ OCR processing completed in {int(total_time * 1000)}ms")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"💥 OCR processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
    
    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file size
        if not self.file_validator.validate_file_size(file, settings.MAX_FILE_SIZE):
            size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {size_mb}MB"
            )
        
        # Check file type
        if not self.file_validator.validate_file_type(file, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        logger.info(f"✅ File validation passed: {file.filename}")
    
    async def _process_image(
        self, 
        file: UploadFile, 
        model: str, 
        language: str, 
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process image file"""
        try:
            logger.info(f"🖼️ Processing image: {file.filename}")
            
            # Validate image
            is_valid, info = await self.image_processor.validate_image(file)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid image: {info}")
            
            # Prepare image for Gemini
            image = await self.image_processor.prepare_image_for_gemini(file)
            
            # Extract text
            result = await gemini_service.extract_text_from_image(
                image, model, language, file.filename or "image"
            )
            
            logger.info(f"✅ Image processing completed: {file.filename}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Image processing failed: {str(e)}")
            raise
    
    async def _process_pdf(
        self, 
        file: UploadFile, 
        model: str, 
        language: str, 
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process PDF file"""
        try:
            logger.info(f"📄 Processing PDF: {file.filename}")
            
            # Validate PDF
            is_valid, info = await self.pdf_processor.validate_pdf(file)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Invalid PDF: {info}")
            
            # Convert PDF to images
            images = await self.pdf_processor.pdf_to_images(file, max_pages=10)
            
            if not images:
                raise HTTPException(status_code=400, detail="No pages found in PDF")
            
            # Extract text from all pages
            result = await gemini_service.extract_text_from_pdf_pages(
                images, model, language, file.filename or "document.pdf"
            )
            
            logger.info(f"✅ PDF processing completed: {file.filename}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ PDF processing failed: {str(e)}")
            raise
    
    def _create_metadata(
        self, 
        file_info: Dict[str, Any], 
        result: Dict[str, Any], 
        model: str, 
        language: str
    ) -> Dict[str, Any]:
        """Create metadata for OCR result"""
        metadata = {
            "model": model,
            "api_key_name": result.get("api_key_used", "unknown"),
            "language": language,
            "filename": file_info["filename"],
            "file_type": file_info["actual_mime_type"],
            "file_size": file_info["size"],
            "file_size_formatted": format_file_size(file_info["size"]),
            "pages": result.get("pages_processed", 1),
            "words": result.get("word_count", 0),
            "characters": result.get("char_count", 0),
            "timestamp": datetime.now().isoformat(),
            "processing_details": {
                "gemini_processing_time_ms": result.get("processing_time_ms", 0),
                "model_used": result.get("model_used", model),
                "confidence": result.get("confidence", 0.0)
            }
        }
        
        # Add page-specific details for PDFs
        if "page_results" in result:
            metadata["page_details"] = result["page_results"]
        
        return metadata
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """Get supported file formats"""
        return {
            "images": {
                "mime_types": self.supported_image_types,
                "extensions": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"],
                "max_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
            },
            "documents": {
                "mime_types": self.supported_document_types,
                "extensions": [".pdf"],
                "max_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024),
                "max_pages": 10
            }
        }
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get available AI models"""
        models = gemini_service.get_available_models()
        return {
            "models": models,
            "default": "gemini-2.5-flash",
            "recommended": {
                "speed": "gemini-2.5-flash",
                "accuracy": "gemini-2.5-pro",
                "balanced": "gemini-2.5-flash"
            }
        }
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health information"""
        try:
            gemini_stats = gemini_service.get_service_stats()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "gemini": gemini_stats,
                    "file_processing": {
                        "supported_formats": len(self.supported_image_types + self.supported_document_types),
                        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
                    }
                }
            }
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global service instance
ocr_service = OCRService() 