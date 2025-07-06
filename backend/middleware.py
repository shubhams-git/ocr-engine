"""
Simple error handling middleware
"""
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)

async def error_handler(request: Request, call_next):
    """Simple error handling middleware"""
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        # Let FastAPI handle HTTP exceptions normally
        raise
    except RequestValidationError:
        # Let FastAPI handle validation errors normally
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in {request.method} {request.url}: {str(e)}")
        
        # Return a generic error response
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
        ) 