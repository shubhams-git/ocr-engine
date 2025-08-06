from typing import Optional, List, Tuple

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from logging_config import get_logger
from services.stage1_cache_service import stage2_from_two_csvs

router = APIRouter()
logger = get_logger(__name__)


@router.post("/test/stage2")
async def test_stage2_endpoint(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    model: Optional[str] = Form(None),
):
    try:
        content1 = await file1.read()
        content2 = await file2.read()

        # Ensure filenames are non-None strings for typing compatibility
        fname1: str = file1.filename or "file1.csv"
        fname2: str = file2.filename or "file2.csv"

        files_data: List[Tuple[str, bytes]] = [
            (fname1, content1),
            (fname2, content2),
        ]

        result = await stage2_from_two_csvs(files_data, model)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"/test/stage2 failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")