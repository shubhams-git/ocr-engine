"""
Enhanced Analysis Service - Stage 3.5: Strategic Enhancement & External Factor Analysis
"""
import asyncio
import time
import json
from typing import Dict, Any

from google import genai
from config import get_next_key, API_TIMEOUT, MAX_RETRIES, BASE_RETRY_DELAY
from prompts import STAGE3_5_ENHANCEMENT_PROMPT
from logging_config import get_logger, log_api_call, log_stage_progress
from services.utils import SuperRobustJSONParser

logger = get_logger(__name__)

class EnhancementService:
    """
    Service for Stage 3.5: Strategic Enhancement & External Factor Analysis
    """
    def __init__(self):
        self.api_timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.base_retry_delay = BASE_RETRY_DELAY

    async def enhance_analysis(self, stage3_result: Dict, model: str = "gemini-1.5-pro-latest") -> Dict[str, Any]:
        """
        Enhance the business analysis with strategic insights and external factors.
        """
        log_stage_progress(logger, "3.5", "Enhancing analysis", "Strategic Enhancement & External Factor Analysis")
        default_return = {"enhancement_factors": []}

        try:
            # Prepare the prompt
            prompt = STAGE3_5_ENHANCEMENT_PROMPT.replace(
                '{stage3_comprehensive_analysis}', json.dumps(stage3_result, indent=2)
            )

            # Call the Gemini API
            response_text = await self._call_gemini_api(prompt, model)

            # Parse the response
            enhancement_factors = SuperRobustJSONParser.parse_gemini_response(response_text)

            if enhancement_factors and isinstance(enhancement_factors, dict):
                return enhancement_factors
            else:
                logger.warning("Parsing of enhancement factors failed or returned empty. Returning default value.")
                return default_return

        except Exception as e:
            logger.error(f"An unexpected error occurred in enhance_analysis: {e}", exc_info=True)
            return default_return

    async def _call_gemini_api(self, prompt: str, model: str) -> str:
        """
        Call the Gemini API with retry logic.
        """
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                api_key = get_next_key()
                client = genai.Client(api_key=api_key)
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=model,
                        contents=prompt
                    ),
                    timeout=self.api_timeout
                )
                
                if response.text:
                    return response.text
                raise Exception("Empty response from API")
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.base_retry_delay * (2 ** attempt))
                else:
                    raise e
        raise Exception(f"All retries failed. Last exception: {last_exception}")

enhancement_service = EnhancementService()