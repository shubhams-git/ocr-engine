"""
Utility functions for file handling and validation
"""
import os
import logging
from typing import Tuple, Optional, TYPE_CHECKING
from fastapi import UploadFile, HTTPException
import io

# Type checking imports
if TYPE_CHECKING:
    import fitz
    from PIL import Image

# Optional imports with fallbacks
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import fitz  # PyMuPDF
    # Test if PyMuPDF works by creating a simple document
    test_doc = fitz.Document()
    test_doc.close()
    HAS_PYMUPDF = True
except (ImportError, Exception):
    HAS_PYMUPDF = False
    print("⚠️ PyMuPDF not available or causing issues. PDF processing will be disabled.")

logger = logging.getLogger(__name__)

class FileValidator:
    """File validation utilities"""
    
    @staticmethod
    def validate_file_size(file: UploadFile, max_size: int) -> bool:
        """Validate file size"""
        if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
            # Get current position
            current_pos = file.file.tell()
            # Seek to end to get size
            file.file.seek(0, 2)
            file_size = file.file.tell()
            # Reset position
            file.file.seek(current_pos)
            
            if file_size > max_size:
                logger.warning(f"📁 File too large: {file.filename} ({file_size} bytes > {max_size} bytes)")
                return False
            
        logger.info(f"📁 File size validated: {file.filename}")
        return True
    
    @staticmethod
    def validate_file_type(file: UploadFile, allowed_extensions: list) -> bool:
        """Validate file type by extension and MIME type"""
        if not file.filename:
            return False
            
        # Check extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            logger.warning(f"📁 Invalid file extension: {file.filename} ({file_ext})")
            return False
        
        # Additional MIME type validation could be added here
        logger.info(f"📁 File type validated: {file.filename} ({file_ext})")
        return True
    
    @staticmethod
    async def get_file_info(file: UploadFile) -> dict:
        """Get comprehensive file information"""
        file_content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        info = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(file_content),
            "extension": os.path.splitext(file.filename)[1].lower() if file.filename else "",
        }
        
        # Try to determine actual file type
        try:
            # Using python-magic for better file type detection
            actual_mime = magic.from_buffer(file_content, mime=True)
            info["actual_mime_type"] = actual_mime
        except:
            info["actual_mime_type"] = file.content_type
        
        logger.info(f"📁 File info gathered: {info}")
        return info

class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    async def validate_image(file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate and get image information"""
        try:
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Try to open with PIL
            image = Image.open(io.BytesIO(file_content))
            
            logger.info(f"🖼️ Image validated: {file.filename} ({image.format}, {image.size})")
            return True, f"{image.format} {image.size[0]}x{image.size[1]}"
            
        except Exception as e:
            logger.error(f"🖼️ Image validation failed: {file.filename} - {str(e)}")
            return False, str(e)
    
    @staticmethod
    async def prepare_image_for_gemini(file: UploadFile) -> Image.Image:
        """Prepare image for Gemini API processing"""
        try:
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if image.mode in ('RGBA', 'LA', 'P'):
                from typing import cast
                background = Image.new('RGB', image.size, cast(int, 255))  # White background
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (Gemini has size limits)
            max_size = (4096, 4096)  # Gemini's max dimensions
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                logger.info(f"🖼️ Resizing large image: {image.size} -> fit in {max_size}")
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            logger.info(f"🖼️ Image prepared for Gemini: {file.filename}")
            return image
            
        except Exception as e:
            logger.error(f"🖼️ Failed to prepare image: {file.filename} - {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

class PDFProcessor:
    """PDF processing utilities"""
    
    @staticmethod
    async def validate_pdf(file: UploadFile) -> Tuple[bool, Optional[str]]:
        """Validate PDF file"""
        if not HAS_PYMUPDF:
            return False, "PDF processing not available (PyMuPDF not working)"
            
        try:
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Try to open with PyMuPDF
            pdf_doc = fitz.Document(stream=file_content, filetype="pdf")
            page_count = pdf_doc.page_count
            pdf_doc.close()
            
            logger.info(f"📄 PDF validated: {file.filename} ({page_count} pages)")
            return True, f"{page_count} pages"
            
        except Exception as e:
            logger.error(f"📄 PDF validation failed: {file.filename} - {str(e)}")
            return False, str(e)
    
    @staticmethod
    async def pdf_to_images(file: UploadFile, max_pages: int = 10) -> list:
        """Convert PDF pages to images for Gemini processing"""
        if not HAS_PYMUPDF:
            raise HTTPException(status_code=400, detail="PDF processing not available (PyMuPDF not working)")
            
        try:
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            pdf_doc = fitz.Document(stream=file_content, filetype="pdf")
            images = []
            
            total_pages = min(pdf_doc.page_count, max_pages)
            logger.info(f"📄 Converting PDF to images: {file.filename} ({total_pages} pages)")
            
            for page_num in range(total_pages):
                page = pdf_doc.load_page(page_num)
                
                # Render page to image with high DPI for better OCR
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image
                image = Image.open(io.BytesIO(img_data))
                images.append(image)
                
                logger.info(f"📄 Converted page {page_num + 1}/{total_pages}")
            
            pdf_doc.close()
            logger.info(f"📄 PDF conversion completed: {len(images)} images")
            return images
            
        except Exception as e:
            logger.error(f"📄 PDF conversion failed: {file.filename} - {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")

# File processing factory
class FileProcessorFactory:
    """Factory for creating appropriate file processors"""
    
    @staticmethod
    def get_processor(file_type: str):
        """Get appropriate processor for file type"""
        if file_type.startswith('image/'):
            return ImageProcessor()
        elif file_type == 'application/pdf':
            return PDFProcessor()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")

# Utility functions
def safe_filename(filename: str) -> str:
    """Create a safe filename for storage"""
    import re
    import uuid
    
    # Remove unsafe characters
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Add UUID prefix to avoid conflicts
    name_part, ext = os.path.splitext(safe_name)
    return f"{uuid.uuid4().hex[:8]}_{name_part}{ext}"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    size_float = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_float < 1024.0:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.1f} TB" 