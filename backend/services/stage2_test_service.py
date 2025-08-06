import asyncio
import json
from typing import List, Tuple, Dict, Any, Optional, cast

from fastapi import HTTPException

from google import genai
from google.genai import types

from logging_config import get_logger, log_stage_progress
from config import get_next_key
from prompts import STAGE2_CASH_FLOW_RECONSTRUCTION_PROMPT
from utils import DataStructureParser, JSONValidator
from services.ocr_service import ocr_service
from services.multi_pdf_service import GeminiCacheManager
from models import OCRResponse

logger = get_logger(__name__)


class Stage2TestService:
    def __init__(self) -> None:
        # Enforce CSV max consistent with multi_pdf_service
        self.max_csv_size = 25 * 1024 * 1024  # 25MB
        self.cache_manager = GeminiCacheManager()

    def validate_two_csv(self, files_data: List[Tuple[str, bytes]]) -> None:
        if not files_data or len(files_data) != 2:
            raise HTTPException(status_code=400, detail="Exactly two CSV files are required (P&L and Balance Sheet).")
        for filename, content in files_data:
            if not filename or not filename.lower().endswith(".csv"):
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {filename}. Only CSV is allowed for this endpoint.")
            if len(content) == 0:
                raise HTTPException(status_code=400, detail=f"File is empty: {filename}")
            if len(content) > self.max_csv_size:
                raise HTTPException(status_code=413, detail=f"CSV {filename} too large (max 25MB)")

    async def run_stage1_and_cache(
        self,
        files_data: List[Tuple[str, bytes]],
        extraction_model: str = "gemini-2.5-pro"
    ) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Run Stage 1 for two CSVs and cache the validated normalized data.
        Returns:
          - pnl_cache_key, bs_cache_key
          - pnl_data, bs_data (the exact normalized dicts stored in cache)
        """
        # Run Stage 1 extraction for each CSV using OCR service
        tasks = [
            ocr_service.process_ocr(content, filename, extraction_model)
            for filename, content in files_data
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
                logger.error(f"Stage 1 exception during CSV extraction: {str(res)}")
                continue

            ocr_res = cast(OCRResponse, res)
            if not ocr_res.success:
                logger.error(f"Stage 1 OCR failed: {ocr_res.error or 'Unknown error'}")
                continue

            try:
                # OCRResponse.data is a JSON string (when success True)
                raw_obj = json.loads(ocr_res.data)
            except Exception:
                # If parsing fails, try robust normalization from string
                try:
                    normalized_try = DataStructureParser.normalize_stage1_result({"success": True, "data": ocr_res.data, "error": None})
                    raw_obj = normalized_try.get("data")
                    if isinstance(raw_obj, str):
                        raw_obj = json.loads(raw_obj)
                except Exception as e:
                    logger.error(f"Failed to interpret Stage 1 output as JSON: {str(e)}")
                    continue

            # Normalize structure similar to multi_pdf_service
            normalized = DataStructureParser.normalize_stage1_result({"success": True, "data": raw_obj, "error": None})
            data = normalized.get("data")

            is_valid = False
            if data:
                is_valid = JSONValidator.validate_financial_data(data)

            if not is_valid:
                logger.warning("Financial data validation failed for a CSV input")
                continue

            document_type = (data or {}).get("document_type", "Other")
            detected_any = True
            if document_type == "Profit and Loss":
                detected_pnl = True
            # Guard against None data before accessing .get
            safe_data = data or {}
            periods_len = len(safe_data.get('periods', []))
            if data is None:
                logger.warning(f"Detected document_type={document_type} but data is None; periods treated as 0 for logging")
            logger.info(f"Detected document_type={document_type} with {periods_len} periods")

            # Create cache for P&L or BS using same manager
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

        # Validation rules
        if not detected_any:
            raise HTTPException(status_code=400, detail="No recognizable financial data found in provided CSV files.")
        if not detected_pnl:
            raise HTTPException(status_code=400, detail="No Profit & Loss statement detected. P&L is required for Stage 2 reconstruction.")
        # BS optional; proceed with P&L-only while warning
        if not bs_cache_key:
            logger.warning("Balance Sheet not detected; proceeding with P&L only. Some Stage 2 elements may be limited.")

        return pnl_cache_key, bs_cache_key, pnl_data, bs_data

    async def run_stage2(
        self, 
        pnl_cache_key: Optional[str], 
        bs_cache_key: Optional[str],
        pnl_data: Optional[Dict[str, Any]],
        bs_data: Optional[Dict[str, Any]], 
        requested_model: Optional[str]
    ) -> Dict[str, Any]:
        """
        Stage 2: Properly use cached content for cash flow reconstruction
        """
        # Coerce analysis model to Pro if non-Pro provided
        model = (requested_model or "gemini-2.5-pro")
        if "pro" not in model.lower():
            model = "gemini-2.5-pro"

        # Log data availability
        pnl_periods = len(pnl_data.get('periods', [])) if pnl_data else 0
        bs_periods = len(bs_data.get('periods', [])) if bs_data else 0
        logger.info(f"Stage 2 Input Data: P&L={pnl_periods} periods, BS={bs_periods} periods")

        # Prepare Gemini client with API key rotation
        api_key = get_next_key()
        client = genai.Client(api_key=api_key)

        # Determine if we can use cached content
        use_cached_content = (
            pnl_cache_key and 
            not pnl_cache_key.startswith("cache_failed") and
            not pnl_cache_key.startswith("cache_creation_failed")
        )

        log_stage_progress(logger, "2", "STARTED", 
                          f"Cash Flow Reconstruction | Model: {model} | "
                          f"Cache: {'ENABLED' if use_cached_content else 'DISABLED'} | "
                          f"Expected periods: {max(pnl_periods, bs_periods)}")

        try:
            if use_cached_content:
                # CRITICAL FIX: Use cached content properly
                logger.info(f"Using cached content approach with P&L cache: {pnl_cache_key}")
                
                # Build prompt that references the cached content
                prompt = STAGE2_CASH_FLOW_RECONSTRUCTION_PROMPT
                # Don't substitute cache keys in prompt - they're for reference only
                prompt = prompt.replace("$pnl_cache_key", pnl_cache_key or "not_available")
                prompt = prompt.replace("$bs_cache_key", bs_cache_key or "not_available")
                
                # Add explicit instruction about expected periods
                prompt += f"\n\nCRITICAL: The P&L data contains {pnl_periods} periods and the Balance Sheet contains {bs_periods} periods. You MUST generate cash flow data for ALL {max(pnl_periods, bs_periods)} periods. Do not skip any periods."
                
                # Use cached content in the API call
                generation_config = types.GenerateContentConfig(
                    cached_content=pnl_cache_key,  # CRITICAL: Use the cached content!
                    response_mime_type="application/json"
                )
                
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=model,
                    contents=prompt,
                    config=generation_config
                )
            else:
                # Fallback: Include actual data in the prompt if caching failed
                logger.warning("Cache not available, using direct data approach")
                
                # Build prompt with actual data
                prompt = STAGE2_CASH_FLOW_RECONSTRUCTION_PROMPT
                prompt = prompt.replace("$pnl_cache_key", "direct_data_mode")
                prompt = prompt.replace("$bs_cache_key", "direct_data_mode")
                
                # Prepare combined data for processing
                combined_data = {
                    "pnl_data": pnl_data,
                    "bs_data": bs_data,
                    "total_periods_expected": max(pnl_periods, bs_periods)
                }
                
                # Add explicit instruction
                prompt += f"\n\nCRITICAL: Process ALL {max(pnl_periods, bs_periods)} periods from the provided data. Do not generate sample data."
                
                # Include the actual data in the prompt
                full_prompt = f"{json.dumps(combined_data, indent=2)}\n\n{prompt}"
                
                generation_config = types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
                
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=model,
                    contents=full_prompt,
                    config=generation_config
                )

            # Extract and parse response
            text = ""
            if hasattr(response, "text") and response.text:
                text = response.text.strip()
            elif hasattr(response, "candidates") and response.candidates:
                cand = response.candidates[0]
                content_obj = getattr(cand, "content", None)
                parts = getattr(content_obj, "parts", None) if content_obj is not None else None
                if isinstance(parts, list) and len(parts) > 0:
                    first_part = parts[0]
                    part_text = getattr(first_part, "text", None)
                    if isinstance(part_text, str):
                        text = part_text.strip()

            # Parse JSON response
            try:
                result = json.loads(text)
                
                # Validate we got all periods
                generated_periods = len(result.get('periods', []))
                expected_periods = max(pnl_periods, bs_periods)
                
                if generated_periods < expected_periods:
                    logger.error(f"⚠️ DATA LOSS: Only {generated_periods}/{expected_periods} periods generated!")
                    result['data_quality_warning'] = f"Only {generated_periods} of {expected_periods} periods were processed"
                    
                    # Adjust quality score for data loss
                    if 'quality' in result:
                        original_score = result['quality'].get('global_score', 0)
                        coverage_ratio = generated_periods / expected_periods if expected_periods > 0 else 0
                        adjusted_score = original_score * coverage_ratio
                        result['quality']['global_score'] = adjusted_score
                        result['quality']['data_coverage'] = coverage_ratio
                        result['quality']['periods_missing'] = expected_periods - generated_periods
                        logger.info(f"Adjusted quality score from {original_score:.2f} to {adjusted_score:.2f} due to {(1-coverage_ratio)*100:.0f}% data loss")
                else:
                    logger.info(f"✅ Successfully generated all {generated_periods} periods")
                    
            except Exception as e:
                logger.error(f"Stage 2 JSON parsing failed: {str(e)} | First 200 chars: {text[:200]}")
                raise HTTPException(status_code=502, detail="Failed to parse Stage 2 model JSON response")

            log_stage_progress(logger, "2", "COMPLETED", 
                             f"Cash Flow Reconstruction complete | Periods: {generated_periods}/{expected_periods}")
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Stage 2 generation failed: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Stage 2 generation failed: {str(e)}")


stage2_test_service = Stage2TestService()


async def stage2_from_two_csvs(files_data: List[Tuple[str, bytes]], requested_model: Optional[str]) -> Dict[str, Any]:
    """
    Fixed version that properly uses cached content
    """
    logger.info("Stage2 Test: validating exactly two CSV files")
    stage2_test_service.validate_two_csv(files_data)

    # Stage 1 using fixed gemini-2.5-pro per instructions
    log_stage_progress(logger, "1", "STARTED", "Stage 1 extraction for two CSVs (gemini-2.5-pro)")
    pnl_cache_key, bs_cache_key, pnl_data, bs_data = await stage2_test_service.run_stage1_and_cache(
        files_data, extraction_model="gemini-2.5-pro"
    )
    log_stage_progress(logger, "1", "COMPLETED", 
                      f"Cache keys -> P&L: {pnl_cache_key} | BS: {bs_cache_key or 'none'}")

    # Stage 2 with proper cache usage - pass the data too!
    result = await stage2_test_service.run_stage2(
        pnl_cache_key, bs_cache_key, pnl_data, bs_data, requested_model
    )
    
    # Include Stage 1 data in response for validation
    return {
        "stage1": {
            "pnl": pnl_data,
            "balance_sheet": bs_data,
        },
        "cache_keys": {
            "pnl": pnl_cache_key,
            "balance_sheet": bs_cache_key,
        },
        "cash_flow": result
    }