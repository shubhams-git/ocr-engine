"""
Minimal OCR API Server using Google Gemini AI
"""
import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import new Google GenAI SDK
from google import genai
from google.genai import types

from config import get_next_key, get_current_key, API_KEYS, ALLOWED_ORIGINS
from models import OCRResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="OCR API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize GenAI client with current API key
client = genai.Client(api_key=get_current_key())

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "OCR API"}

@app.get("/models")
async def get_available_models():
    """Get available Gemini models"""
    models = [
        {
            "id": "gemini-2.5-pro",
            "name": "Gemini 2.5 Pro",
            "description": "Most capable model for complex tasks"
        },
        {
            "id": "gemini-2.5-flash", 
            "name": "Gemini 2.5 Flash",
            "description": "Fast and efficient (Recommended)"
        },
        {
            "id": "gemini-2.0-flash",
            "name": "Gemini 2.0 Flash", 
            "description": "Latest experimental model"
        },
        {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "description": "Fast and reliable"
        },
        {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "description": "Advanced reasoning capabilities"
        }
    ]
    return {
        "models": models,
        "default": "gemini-2.5-flash"
    }

@app.get("/api-keys/status")
async def get_api_key_status():
    """Get API key rotation status"""
    from config import current_key_index
    return {
        "total_keys": len(API_KEYS),
        "current_key_index": current_key_index,
        "rotation_enabled": True
    }

@app.post("/api-keys/rotate")
async def rotate_api_key():
    """Manually rotate to the next API key"""
    get_next_key()  # This will rotate the key
    from config import current_key_index
    return {
        "message": "API key rotated successfully",
        "current_key_index": current_key_index,
        "total_keys": len(API_KEYS)
    }

@app.post("/ocr", response_model=OCRResponse)
async def process_ocr(file: UploadFile = File(...), model: str = "gemini-2.5-flash"):
    """Extract data from uploaded PDF file using Gemini AI with API key rotation"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        
        # Validate file size (50MB limit)
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
        
        # Simple prompt for JSON extraction
        prompt = "Extract the accurate data in a json"
        
        # Try with each API key until one works
        last_error = None
        
        for attempt in range(len(API_KEYS)):
            try:
                # Get next API key
                api_key = get_next_key()
                current_client = genai.Client(api_key=api_key)
                
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
                if response and hasattr(response, 'text') and response.text:
                    return OCRResponse(success=True, data=response.text.strip(), error=None)
                elif response and hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            text_part = candidate.content.parts[0].text
                            if text_part:
                                return OCRResponse(success=True, data=text_part.strip(), error=None)
                
                # If we get here, no valid response was extracted
                raise Exception("No data could be extracted from response")
                
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 