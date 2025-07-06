"""
Admin endpoints for API key management
"""
from fastapi import APIRouter
from config import get_next_key, API_KEYS

router = APIRouter(prefix="/api-keys", tags=["admin"])

@router.get("/status")
async def get_api_key_status():
    """Get API key rotation status"""
    from config import current_key_index
    return {
        "total_keys": len(API_KEYS),
        "current_key_index": current_key_index,
        "rotation_enabled": True
    }

@router.post("/rotate")
async def rotate_api_key():
    """Manually rotate to the next API key"""
    get_next_key()  # This will rotate the key
    from config import current_key_index
    return {
        "message": "API key rotated successfully",
        "current_key_index": current_key_index,
        "total_keys": len(API_KEYS)
    } 