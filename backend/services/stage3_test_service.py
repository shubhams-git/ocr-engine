import asyncio
import json
from typing import Dict, Any, Optional, Tuple, List, cast

from fastapi import HTTPException

from logging_config import get_logger, log_stage_progress
from config import get_next_key
from utils import DataStructureParser, JSONValidator
from models import OCRResponse
from services.ocr_service import ocr_service
from services.multi_pdf_service import GeminiCacheManager
from services.business_analysis_service import business_analysis_service
from services.projection_service import projection_service

logger = get_logger(__name__)


class Stage3TestService:
    """
    Service to run end-to-end Stage 1 -> Stage 2 -> Stage 3 for testing with two inputs:
      - file1: Profit & Loss (CSV/PDF supported by OCR service)
      - file2: Balance Sheet (CSV/PDF supported by OCR service)

    Behavior:
      1) Stage 1: OCR/Normalize both files; cache results individually; capture pl_key and bs_key.
      2) Stage 2: Use Business Analysis Service to reconstruct cash flows from the Stage 1 results,
                  leveraging the cache keys; capture cashflow_key if produced (not currently persisted,
                  so we propagate the dict).
      3) Stage 3: Use Projection Service to generate projections based on Stage 2 output using the
                  same model; return the projections as a dict.
    """

    def __init__(self) -> None:
        # Align with existing services and limits (CSV max 25MB used elsewhere)
        self.max_csv_size = 25 * 1024 * 1024
        self.max_pdf_size = 50 * 1024 * 1024
        self.cache_manager = GeminiCacheManager()

    def _validate_input_pair(self, file1_name: str, file1_bytes: bytes, file2_name: str, file2_bytes: bytes) -> None:
        if not file1_name or not file2_name:
            raise HTTPException(status_code=400, detail="Both files must include filenames.")
        if not file1_bytes or not file2_bytes:
            raise HTTPException(status_code=400, detail="Both files must contain data.")

        # Size checks (honor limits used elsewhere)
        if file1_name.lower().endswith(".csv") and len(file1_bytes) > self.max_csv_size:
            raise HTTPException(status_code=413, detail=f"CSV {file1_name} too large (max 25MB)")
        if file2_name.lower().endswith(".csv") and len(file2_bytes) > self.max_csv_size:
            raise HTTPException(status_code=413, detail=f"CSV {file2_name} too large (max 25MB)")
        if file1_name.lower().endswith(".pdf") and len(file1_bytes) > self.max_pdf_size:
            raise HTTPException(status_code=413, detail=f"PDF {file1_name} too large (max 50MB)")
        if file2_name.lower().endswith(".pdf") and len(file2_bytes) > self.max_pdf_size:
            raise HTTPException(status_code=413, detail=f"PDF {file2_name} too large (max 50MB)")

    async def _run_stage1_and_cache_pair(
        self,
        file1_name: str,
        file1_bytes: bytes,
        file2_name: str,
        file2_bytes: bytes,
        extraction_model: str,
    ) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Mirror Stage 1 logic used by Stage2 test service:
          - OCR both files in parallel
          - Normalize and validate
          - Cache individually for P&L and Balance Sheet
        Returns: (pnl_cache_key, bs_cache_key, pnl_data, bs_data)
        """
        tasks = [
            ocr_service.process_ocr(file1_bytes, file1_name, extraction_model),
            ocr_service.process_ocr(file2_bytes, file2_name, extraction_model),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        pnl_cache_key: Optional[str] = None
        bs_cache_key: Optional[str] = None
        pnl_data: Optional[Dict[str, Any]] = None
        bs_data: Optional[Dict[str, Any]] = None

        detected_any = False
        detected_pnl = False

        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Stage 1 exception during extraction: {str(res)}")
                continue

            ocr_res = cast(OCRResponse, res)
            if not ocr_res.success:
                logger.error(f"Stage 1 OCR failed: {ocr_res.error or 'Unknown error'}")
                continue

            # Parse OCR response into JSON object safely
            try:
                raw_obj = json.loads(ocr_res.data)
            except Exception:
                try:
                    normalized_try = DataStructureParser.normalize_stage1_result(
                        {"success": True, "data": ocr_res.data, "error": None}
                    )
                    raw_obj = normalized_try.get("data")
                    if isinstance(raw_obj, str):
                        raw_obj = json.loads(raw_obj)
                except Exception as e:
                    logger.error(f"Failed to interpret Stage 1 output as JSON: {str(e)}")
                    continue

            # Normalize and validate
            normalized = DataStructureParser.normalize_stage1_result({"success": True, "data": raw_obj, "error": None})
            data = normalized.get("data")

            is_valid = False
            if data:
                is_valid = JSONValidator.validate_financial_data(data)

            if not is_valid:
                logger.warning("Financial data validation failed for an input")
                continue

            document_type = (data or {}).get("document_type", "Other")
            detected_any = True
            if document_type == "Profit and Loss":
                detected_pnl = True

            safe_data = data or {}
            periods_len = len(safe_data.get("periods", []))
            if data is None:
                logger.warning(
                    f"Detected document_type={document_type} but data is None; periods treated as 0 for logging"
                )
            logger.info(f"Detected document_type={document_type} with {periods_len} periods")

            # Cache creation for P&L / BS
            if document_type in ["Profit and Loss", "Balance Sheet"]:
                try:
                    key = get_next_key()
                    cache_payload: Dict[str, Any] = dict(data) if isinstance(data, dict) else {}
                    cache_name = await self.cache_manager.create_cache_for_stage1_result(cache_payload, key, document_type)
                    if document_type == "Profit and Loss":
                        pnl_cache_key = cache_name or pnl_cache_key
                        pnl_data = cache_payload
                        logger.info(f"P&L cache created: {pnl_cache_key} with {len(cache_payload.get('periods', []))} periods")
                    elif document_type == "Balance Sheet":
                        bs_cache_key = cache_name or bs_cache_key
                        bs_data = cache_payload
                        logger.info(f"BS cache created: {bs_cache_key} with {len(cache_payload.get('periods', []))} periods")
                except Exception as e:
                    logger.warning(f"Cache creation failed for {document_type}: {str(e)}")

        # Enforce presence
        if not detected_any:
            raise HTTPException(status_code=400, detail="No recognizable financial data found in provided files.")
        if not detected_pnl:
            raise HTTPException(status_code=400, detail="No Profit & Loss statement detected. P&L is required.")

        # BS is optional; proceed with warning if missing
        if not bs_cache_key:
            logger.warning("Balance Sheet not detected; proceeding with P&L only.")

        return pnl_cache_key, bs_cache_key, pnl_data, bs_data

    async def _run_stage2_cash_flow(
        self,
        pnl_cache_key: Optional[str],
        bs_cache_key: Optional[str],
        pnl_data: Optional[Dict[str, Any]],
        bs_data: Optional[Dict[str, Any]],
        requested_model: Optional[str],
    ) -> Dict[str, Any]:
        """
        Use business_analysis_service with proper cache usage to generate cash flows.
        Returns the cash flow dict produced by the service.
        """
        # Coerce to Pro for analysis if needed
        model = (requested_model or "gemini-2.5-pro")
        if "pro" not in (model or "").lower():
            model = "gemini-2.5-pro"

        # Compose stage1_results list expected by analyze_business_context
        stage1_results: List[Dict[str, Any]] = []
        if pnl_data:
            stage1_results.append({"success": True, "data": pnl_data, "error": None})
        if bs_data:
            stage1_results.append({"success": True, "data": bs_data, "error": None})

        if not stage1_results:
            raise HTTPException(status_code=400, detail="Stage 2 cannot proceed without any valid Stage 1 data.")

        log_stage_progress(logger, "2", "STARTED", f"Cash Flow Reconstruction | Model: {model}")
        try:
            result = await business_analysis_service.analyze_business_context(
                stage1_results, model=model, pnl_cache_key=pnl_cache_key, bs_cache_key=bs_cache_key
            )
            # Log completeness
            generated_periods = len(result.get("periods", [])) if isinstance(result, dict) else 0
            expected_periods = max(
                len((pnl_data or {}).get("periods", [])),
                len((bs_data or {}).get("periods", [])),
            )
            log_stage_progress(
                logger,
                "2",
                "COMPLETED",
                f"Cash Flow Reconstruction complete | Periods: {generated_periods}/{expected_periods}",
            )
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Stage 2 generation failed: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Stage 2 generation failed: {str(e)}")

    async def _run_stage3_projections(
        self,
        pnl_cache_key: Optional[str],
        bs_cache_key: Optional[str],
        cashflow_result: Dict[str, Any],
        requested_model: Optional[str],
    ) -> Dict[str, Any]:
        """
        Use projection_service to generate projections, reusing the same model policy.
        Prefers the legacy generate_projections that consumes stage2_result dict,
        which aligns with current projection_service interface.
        """
        model = (requested_model or "gemini-2.5-pro")
        if "pro" not in (model or "").lower():
            model = "gemini-2.5-pro"

        log_stage_progress(logger, "3", "STARTED", f"Projection Generation | Model: {model}")
        try:
            # Prefer comprehensive projections when cache keys exist to enforce strict JSON output
            parent_keys = cashflow_result.get("parent_keys", {}) if isinstance(cashflow_result, dict) else {}
            pnl_cache_key = parent_keys.get("pnl_cache_key")
            bs_cache_key = parent_keys.get("bs_cache_key")
            cf_cache_key = cashflow_result.get("cache_key")

            projections: Dict[str, Any]
            if pnl_cache_key and bs_cache_key and cf_cache_key and not str(pnl_cache_key).startswith("stage1_") and not str(bs_cache_key).startswith("stage1_"):
                projections = await projection_service.generate_comprehensive_projections(
                    pnl_cache_key=pnl_cache_key,
                    bs_cache_key=bs_cache_key,
                    cf_cache_key=cf_cache_key,
                    model=model,
                )
            else:
                # Fallback to legacy path (now with robust parsing in projection_service)
                projections = await projection_service.generate_projections(cashflow_result, model=model)

            # Ensure dict
            if isinstance(projections, dict):
                projections_dict = projections
            else:
                # Best-effort conversion for unexpected types
                try:
                    projections_dict = dict(projections)  # type: ignore[arg-type]
                except Exception:
                    projections_dict = {}

            log_stage_progress(
                logger,
                "3",
                "COMPLETED",
                f"Projections generated | Base cases: {len(projections_dict.get('base_case_projections', {}))}",
            )
            return projections_dict
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Stage 3 generation failed: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Stage 3 generation failed: {str(e)}")

    async def _run_stage3_from_cache_keys(
        self,
        pnl_cache_key: str,
        bs_cache_key: Optional[str],
        cf_cache_key: str,
        requested_model: Optional[str],
    ) -> Dict[str, Any]:
        """
        New path: Directly run Stage 3 using cache keys without running Stages 1 and 2.
        Validates keys exist in cache, then calls projection engine.
        """
        if not pnl_cache_key or not cf_cache_key:
            raise HTTPException(status_code=400, detail="Both 'pnl_cache_key' and 'cf_cache_key' are required.")

        model = (requested_model or "gemini-2.5-pro")
        if "pro" not in model.lower():
            model = "gemini-2.5-pro"

        # Confirm cache existence (non-blocking checks) by attempting to fetch metadata
        # GeminiCacheManager does not expose 'exists'; use get_cached_content which returns None on failure.
        from config import get_next_key as _get_key_for_cache_lookup

        try:
            _api_key = _get_key_for_cache_lookup()
            pnl_meta = await self.cache_manager.get_cached_content(pnl_cache_key, _api_key)
        except Exception:
            pnl_meta = None
        if not pnl_meta:
            raise HTTPException(status_code=404, detail=f"P&L cache not found for key: {pnl_cache_key}")

        if bs_cache_key:
            try:
                _api_key = _get_key_for_cache_lookup()
                bs_meta = await self.cache_manager.get_cached_content(bs_cache_key, _api_key)
            except Exception:
                bs_meta = None
            if not bs_meta:
                logger.warning(f"BS cache not found for key: {bs_cache_key}; proceeding with P&L only.")
                bs_cache_key = ""

        try:
            _api_key = _get_key_for_cache_lookup()
            cf_meta = await self.cache_manager.get_cached_content(cf_cache_key, _api_key)
        except Exception:
            cf_meta = None
        if not cf_meta:
            raise HTTPException(status_code=404, detail=f"Cash Flow cache not found for key: {cf_cache_key}")

        try:
            projections = await projection_service.generate_comprehensive_projections(
                pnl_cache_key=pnl_cache_key,
                bs_cache_key=bs_cache_key or "",
                cf_cache_key=cf_cache_key,
                model=model,
            )
            return dict(projections) if isinstance(projections, dict) else {"result": projections}
        except Exception as e:
            logger.error(f"Stage 3 generation failed (cache-keys): {str(e)}")
            raise HTTPException(status_code=502, detail=f"Stage 3 generation failed: {str(e)}")


async def run_stage3_test(
    file1_bytes: bytes,
    file1_name: str,
    file2_bytes: bytes,
    file2_name: str,
    model: str,
) -> Dict[str, Any]:
    """
    Orchestrates Stage 1 -> Stage 2 -> Stage 3 for two inputs.

    Args:
        file1_bytes: bytes of first file (expected P&L, but auto-detected)
        file1_name: filename of first file
        file2_bytes: bytes of second file (expected BS, but auto-detected)
        file2_name: filename of second file
        model: model name string; same model used across Stages 2 and 3
    Returns:
        dict containing the final Stage 3 projections (and intermediate keys for traceability)
    """
    svc = Stage3TestService()

    # Validate basic pair constraints
    svc._validate_input_pair(file1_name, file1_bytes, file2_name, file2_bytes)

    # Stage 1
    log_stage_progress(logger, "1", "STARTED", "Stage 1 extraction for two inputs (gemini-2.5-pro)")
    try:
        pnl_key, bs_key, pnl_data, bs_data = await svc._run_stage1_and_cache_pair(
            file1_name, file1_bytes, file2_name, file2_bytes, extraction_model="gemini-2.5-pro"
        )
        log_stage_progress(logger, "1", "COMPLETED", f"Cache keys -> P&L: {pnl_key} | BS: {bs_key or 'none'}")
    except Exception as e:
        # Include any known keys in error message
        msg = f"Stage 1 failed: {str(e)}"
        logger.error(msg)
        raise

    # Stage 2
    try:
        logger.info(f"Stage 2 starting | pl_key={pnl_key} bs_key={bs_key}")
        cash_flows = await svc._run_stage2_cash_flow(pnl_key, bs_key, pnl_data, bs_data, model)
        logger.info(f"Stage 2 completed | cashflow periods={len(cash_flows.get('periods', [])) if isinstance(cash_flows, dict) else 0}")
    except Exception as e:
        msg = f"Stage 2 failed (pl_key={pnl_key}, bs_key={bs_key}): {str(e)}"
        logger.error(msg)
        raise

    # Stage 3
    try:
        logger.info(f"Stage 3 starting | pl_key={pnl_key} bs_key={bs_key}")
        projections = await svc._run_stage3_projections(pnl_key, bs_key, cash_flows, model)
        logger.info("Stage 3 completed")
    except Exception as e:
        msg = f"Stage 3 failed (pl_key={pnl_key}, bs_key={bs_key}): {str(e)}"
        logger.error(msg)
        raise

    # Return exactly what projection service produces (dict), with trace keys for debugging
    result: Dict[str, Any] = dict(projections) if isinstance(projections, dict) else {}
    # Attach cache keys context minimally for traceability (non-invasive)
    result.setdefault("_trace", {})
    result["_trace"]["pl_key"] = pnl_key
    result["_trace"]["bs_key"] = bs_key
    result["_trace"]["cashflow_periods"] = len(cash_flows.get("periods", [])) if isinstance(cash_flows, dict) else 0

    return result


async def run_stage3_from_cache_keys(
    pnl_cache_key: str,
    bs_cache_key: Optional[str],
    cf_cache_key: str,
    model: Optional[str] = "gemini-2.5-pro",
) -> Dict[str, Any]:
    """
    Public service function to run Stage 3 directly from cache keys.
    """
    svc = Stage3TestService()
    projections = await svc._run_stage3_from_cache_keys(
        pnl_cache_key=pnl_cache_key,
        bs_cache_key=bs_cache_key,
        cf_cache_key=cf_cache_key,
        requested_model=model,
    )
    return projections