from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import JSONResponse

from logging_config import get_logger
from services.stage3_test_service import run_stage3_test, run_stage3_from_cache_keys

router = APIRouter()
logger = get_logger(__name__)


@router.post("/test/stage3")
async def test_stage3_endpoint(
    file1: Optional[UploadFile] = File(None),
    file2: Optional[UploadFile] = File(None),
    model: Optional[str] = Form(None),
    cache_keys: Optional[dict] = Body(
        default=None,
        examples=[{"pnl_cache_key": "cachedContents/...", "bs_cache_key": "cachedContents/...", "cf_cache_key": "enhanced_cf_..."}],
    ),
):
    """
    Stage 3 test endpoint.

    Backward-compatible behavior:
      - If file1 and file2 are provided, runs Stage 1 -> Stage 2 -> Stage 3 using the files.

    New behavior:
      - If JSON body contains pnl_cache_key, bs_cache_key, cf_cache_key, bypasses Stages 1 and 2
        and directly invokes Stage 3 projection engine using cached content.
    """
    try:
        # New: cache-keys-first path
        if cache_keys and isinstance(cache_keys, dict):
            pnl_key = cache_keys.get("pnl_cache_key")
            bs_key = cache_keys.get("bs_cache_key")
            cf_key = cache_keys.get("cf_cache_key")

            if not pnl_key or not cf_key:
                raise HTTPException(status_code=400, detail="Missing required cache keys. 'pnl_cache_key' and 'cf_cache_key' are required.")
            # bs_cache_key can be optional for P&L-only flows

            logger.info(f"/test/stage3 start (cache keys) | model={model or 'gemini-2.5-pro'} | keys=(pnl={pnl_key}, bs={bs_key}, cf={cf_key})")

            projections = await run_stage3_from_cache_keys(
                pnl_cache_key=str(pnl_key),
                bs_cache_key=str(bs_key) if bs_key is not None else None,
                cf_cache_key=str(cf_key),
                model=model or "gemini-2.5-pro",
            )
            logger.info(f"/test/stage3 completed (cache keys) | keys=(pnl={pnl_key}, bs={bs_key}, cf={cf_key})")
            return JSONResponse(status_code=200, content=projections)

        # Legacy file-based path (backward compatibility)
        if not file1 or not file2:
            raise HTTPException(
                status_code=400,
                detail="Either provide both files (file1, file2) or a JSON body with pnl_cache_key, bs_cache_key, cf_cache_key."
            )

        # Read bytes
        file1_bytes = await file1.read()
        file2_bytes = await file2.read()

        # Ensure filenames are non-None strings for typing compatibility
        file1_name: str = file1.filename or "file1"
        file2_name: str = file2.filename or "file2"

        logger.info(f"/test/stage3 start (files) | model={model or 'gemini-2.5-pro'} | files=({file1_name}, {file2_name})")

        # Delegate to service (Stage 1 -> Stage 2 -> Stage 3 orchestration)
        projections = await run_stage3_test(
            file1_bytes=file1_bytes,
            file1_name=file1_name,
            file2_bytes=file2_bytes,
            file2_name=file2_name,
            model=model or "gemini-2.5-pro",
        )

        logger.info(f"/test/stage3 completed (files) | files=({file1_name}, {file2_name})")
        # Return exactly what the service returns (dict) without extra wrapping
        return JSONResponse(status_code=200, content=projections)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"/test/stage3 failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")