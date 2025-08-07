from typing import Optional, List, Tuple

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, Request
from fastapi.responses import JSONResponse

from logging_config import get_logger
from services.stage1_cache_service import stage2_from_two_csvs
from services.stage2_test_service import stage2_from_cache_keys

router = APIRouter()
logger = get_logger(__name__)


@router.post("/test/stage2")
async def test_stage2_endpoint(
    request: Request,
    file1: UploadFile = File(None),
    file2: UploadFile = File(None),
    model: Optional[str] = Form(None),
    # Accept explicit JSON fields to avoid ambiguous Body(dict) binding
    pl_cache_key: Optional[str] = Body(default=None),
    bs_cache_key: Optional[str] = Body(default=None),
    # Also accept a dict body for backward compatibility or nested envelopes
    cache_keys: Optional[dict] = Body(default=None),
):
    """
    Modified endpoint:
    - Supports original two-CSV upload flow
    - NEW: Supports bypassing Stage 1 by accepting cache keys in JSON body:
        {
          "pl_cache_key": "cachedContents/...",
          "bs_cache_key": "cachedContents/..."
        }
    When cache_keys are provided, the endpoint ignores file inputs and runs Stage 2 directly.
    """
    try:
        # Diagnostic logging with raw body peek for binding issues
        try:
            content_type = request.headers.get("content-type")
            body_bytes = await request.body()
            body_preview = body_bytes.decode("utf-8", errors="ignore")[:500]
            logger.info(
                f"/test/stage2 called | ct={content_type} | body_preview={body_preview} | "
                f"files_present: f1={bool(file1)} f2={bool(file2)} | "
                f"model={model!r} | pl_cache_key={pl_cache_key!r} | bs_cache_key={bs_cache_key!r} | "
                f"cache_keys_type={type(cache_keys).__name__} | cache_keys={cache_keys}"
            )
        except Exception as _log_err:
            logger.warning(f"/test/stage2 logging failed: {_log_err}")

        # If explicit fields didn't bind and raw body exists, try parsing JSON manually once
        manual_keys: Optional[dict] = None
        if (pl_cache_key is None and bs_cache_key is None and cache_keys is None):
            try:
                # Use request.json() which reuses cached body in Starlette
                raw_json = await request.json()
                if isinstance(raw_json, dict):
                    if "cache_keys" in raw_json and isinstance(raw_json["cache_keys"], dict):
                        manual_keys = raw_json["cache_keys"]
                    else:
                        manual_keys = raw_json
                    logger.info(f"Manually parsed JSON body for cache keys: {manual_keys}")
            except Exception as parse_err:
                logger.warning(f"Manual JSON parse failed: {parse_err}")

        # Normalize possible nested envelope { "cache_keys": { ... } }
        if isinstance(cache_keys, dict) and "cache_keys" in cache_keys and isinstance(cache_keys["cache_keys"], dict):
            logger.info("Normalizing nested cache_keys envelope from body")
            cache_keys = cache_keys["cache_keys"]

        # Build unified keys from any of the accepted forms
        keys_src: Optional[dict] = None
        if pl_cache_key is not None or bs_cache_key is not None:
            keys_src = {"pl_cache_key": pl_cache_key, "bs_cache_key": bs_cache_key}
        elif isinstance(cache_keys, dict):
            keys_src = cache_keys
        elif isinstance(manual_keys, dict):
            keys_src = manual_keys

        # If cache keys are provided, bypass stage 1 and use cached content
        if isinstance(keys_src, dict):
            pl_key = keys_src.get("pl_cache_key")
            bs_key = keys_src.get("bs_cache_key")
            if not pl_key:
                raise HTTPException(status_code=400, detail="pl_cache_key is required when using cache_keys mode")

            result = await stage2_from_cache_keys(pl_key, bs_key, model)
            return JSONResponse(status_code=200, content=result)

        # Fallback to original behavior requiring two CSVs
        if not file1 or not file2:
            raise HTTPException(status_code=400, detail="Either provide both CSV files (file1, file2) or JSON body with pl_cache_key/bs_cache_key")

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