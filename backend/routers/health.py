"""
Health and info endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "OCR API"}

@router.get("/models")
async def get_available_models():
    """Get available Gemini models"""
    models = [
        {
            "id": "gemini-2.5-pro",
            "name": "Gemini 2.5 Pro",
            "description": "Most capable model for complex tasks (Recommended)"
        },
        {
            "id": "gemini-2.5-flash", 
            "name": "Gemini 2.5 Flash",
            "description": "Fast and efficient"
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
        "default": "gemini-2.5-pro"
    } 