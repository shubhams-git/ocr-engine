"""
Enhanced configuration for OCR Engine API with Smart Pro Model Fallback
Implements intelligent cooldown periods and Flash model fallback strategy
"""
import os
import threading
from typing import List
from logging_config import get_logger

# Set up logger for configuration
logger = get_logger(__name__)

def get_api_keys() -> List[str]:
    """Get all available API keys from environment variables"""
    keys = []
    
    # Get the main API key (if it exists)
    main_key = os.getenv("GEMINI_API_KEY")
    if main_key:
        keys.append(main_key)
    
    # Get additional keys (GEMINI_API_KEY_1 through GEMINI_API_KEY_10)
    for i in range(1, 11):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
    
    if not keys:
        raise ValueError("No API keys found. Set GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc. in your .env file")
    
    # Use DEBUG level for API key count to reduce startup noise
    logger.debug(f"Loaded {len(keys)} API keys from environment")
    return keys

# Load all available API keys from environment
API_KEYS = get_api_keys()

# Thread-safe key rotation
_key_lock = threading.Lock()
_current_key_index = 0

def get_next_key() -> str:
    """Get the next API key in rotation with thread-safe operation"""
    global _current_key_index
    
    with _key_lock:
        key = API_KEYS[_current_key_index]
        _current_key_index = (_current_key_index + 1) % len(API_KEYS)
        
        # Log which key we're using (last 4 chars for identification)
        key_suffix = key[-4:] if len(key) > 4 else "****"
        logger.debug(f"Using API key ending in ...{key_suffix} (position {_current_key_index}/{len(API_KEYS)})")
        
        return key

def get_current_key() -> str:
    """Get the current API key without rotating"""
    with _key_lock:
        return API_KEYS[_current_key_index]

# ENVIRONMENT VARIABLE GETTERS WITH DEFAULTS
def get_api_timeout() -> int:
    """Get API timeout from environment variable with default fallback"""
    timeout_str = os.getenv("GEMINI_API_TIMEOUT", "720")  # Default: 12 minutes
    try:
        return int(timeout_str)
    except ValueError:
        logger.warning(f"Invalid GEMINI_API_TIMEOUT value: {timeout_str}, using default 720 seconds")
        return 720

def get_overall_process_timeout() -> int:
    """Get overall process timeout from environment variable with default fallback"""
    timeout_str = os.getenv("OVERALL_PROCESS_TIMEOUT", "1200")  # Default: 20 minutes
    try:
        return int(timeout_str)
    except ValueError:
        logger.warning(f"Invalid OVERALL_PROCESS_TIMEOUT value: {timeout_str}, using default 1200 seconds")
        return 1200

def get_max_retries() -> int:
    """Get max retries from environment variable with default fallback"""
    retries_str = os.getenv("GEMINI_MAX_RETRIES", "6")  # Default: 6 retries
    try:
        return int(retries_str)
    except ValueError:
        logger.warning(f"Invalid GEMINI_MAX_RETRIES value: {retries_str}, using default 6")
        return 6

def get_base_retry_delay() -> int:
    """Get base retry delay from environment variable with default fallback"""
    delay_str = os.getenv("GEMINI_BASE_RETRY_DELAY", "15")  # REDUCED: 15 seconds base delay
    try:
        return int(delay_str)
    except ValueError:
        logger.warning(f"Invalid GEMINI_BASE_RETRY_DELAY value: {delay_str}, using default 15 seconds")
        return 15

def get_max_retry_delay() -> int:
    """Get maximum retry delay from environment variable with default fallback"""
    delay_str = os.getenv("GEMINI_MAX_RETRY_DELAY", "120")  # REDUCED: 2 minutes max delay
    try:
        return int(delay_str)
    except ValueError:
        logger.warning(f"Invalid GEMINI_MAX_RETRY_DELAY value: {delay_str}, using default 120 seconds")
        return 120

def get_exponential_multiplier() -> float:
    """Get exponential backoff multiplier from environment variable with default fallback"""
    multiplier_str = os.getenv("GEMINI_EXPONENTIAL_MULTIPLIER", "1.5")  # REDUCED: 1.5x multiplier
    try:
        return float(multiplier_str)
    except ValueError:
        logger.warning(f"Invalid GEMINI_EXPONENTIAL_MULTIPLIER value: {multiplier_str}, using default 1.5")
        return 1.5

def get_overload_multiplier() -> float:
    """Get overload error multiplier from environment variable with default fallback"""
    multiplier_str = os.getenv("GEMINI_OVERLOAD_MULTIPLIER", "2.0")  # REDUCED: 2.0x multiplier
    try:
        return float(multiplier_str)
    except ValueError:
        logger.warning(f"Invalid GEMINI_OVERLOAD_MULTIPLIER value: {multiplier_str}, using default 2.0")
        return 2.0

def get_pro_model_min_delay() -> float:
    """Get Pro model minimum delay from environment variable with default fallback"""
    delay_str = os.getenv("PRO_MODEL_MIN_DELAY", "15.0")  # 15 seconds base cooldown
    try:
        return float(delay_str)
    except ValueError:
        logger.warning(f"Invalid PRO_MODEL_MIN_DELAY value: {delay_str}, using default 15.0 seconds")
        return 15.0

def get_pro_model_error_delay() -> float:
    """Get Pro model post-error delay from environment variable with default fallback"""
    delay_str = os.getenv("PRO_MODEL_ERROR_DELAY", "30.0")  # NEW: 30s after any error
    try:
        return float(delay_str)
    except ValueError:
        logger.warning(f"Invalid PRO_MODEL_ERROR_DELAY value: {delay_str}, using default 30.0 seconds")
        return 30.0

def get_pro_model_overload_delay() -> float:
    """Get Pro model overload delay from environment variable with default fallback"""
    delay_str = os.getenv("PRO_MODEL_OVERLOAD_DELAY", "60.0")  # REDUCED: 1 minute after overload
    try:
        return float(delay_str)
    except ValueError:
        logger.warning(f"Invalid PRO_MODEL_OVERLOAD_DELAY value: {delay_str}, using default 60.0 seconds")
        return 60.0

def get_flash_fallback_threshold() -> int:
    """Get the attempt number when we should start using Flash model fallback"""
    threshold_str = os.getenv("FLASH_FALLBACK_THRESHOLD", "3")  # NEW: Fallback after 2nd retry (3rd attempt)
    try:
        return int(threshold_str)
    except ValueError:
        logger.warning(f"Invalid FLASH_FALLBACK_THRESHOLD value: {threshold_str}, using default 3")
        return 3

# LOAD CONFIGURATION FROM ENVIRONMENT
API_TIMEOUT = get_api_timeout()
OVERALL_PROCESS_TIMEOUT = get_overall_process_timeout()
MAX_RETRIES = get_max_retries()
BASE_RETRY_DELAY = get_base_retry_delay()
MAX_RETRY_DELAY = get_max_retry_delay()
EXPONENTIAL_MULTIPLIER = get_exponential_multiplier()
OVERLOAD_MULTIPLIER = get_overload_multiplier()
PRO_MODEL_MIN_DELAY = get_pro_model_min_delay()
PRO_MODEL_ERROR_DELAY = get_pro_model_error_delay()
PRO_MODEL_OVERLOAD_DELAY = get_pro_model_overload_delay()
FLASH_FALLBACK_THRESHOLD = get_flash_fallback_threshold()

# CORS SETTINGS (from environment with defaults)
def get_allowed_origins() -> List[str]:
    """Get allowed origins from environment with default fallback"""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Default origins
    default_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Add frontend URL from environment if it's not already in defaults
    if frontend_url not in default_origins:
        default_origins.append(frontend_url)
    
    return default_origins

ALLOWED_ORIGINS = get_allowed_origins()

# ENHANCED BUSINESS LOGIC FUNCTIONS
def calculate_smart_backoff_delay(attempt: int, base_delay: float, is_overload: bool = False, had_previous_error: bool = False) -> float:
    """
    Calculate smart backoff delay with reduced timeouts and Flash fallback logic
    
    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        is_overload: Whether this is for a 503 overload error
        had_previous_error: Whether there was a previous error in this session
        
    Returns:
        Calculated delay in seconds
    """
    if is_overload:
        # Overload errors get longer delays but capped lower
        delay = base_delay * OVERLOAD_MULTIPLIER * (EXPONENTIAL_MULTIPLIER ** attempt)
    elif had_previous_error:
        # If we had previous errors, be more conservative
        delay = base_delay * 2 * (EXPONENTIAL_MULTIPLIER ** attempt)
    else:
        # Standard exponential backoff with reduced multiplier
        delay = base_delay * (EXPONENTIAL_MULTIPLIER ** attempt)
    
    # Cap at maximum delay (now much lower)
    return min(delay, MAX_RETRY_DELAY)

def should_use_flash_fallback(attempt: int, is_pro_model: bool) -> bool:
    """
    Determine if we should fallback to Flash model for this attempt
    
    Args:
        attempt: Current attempt number (0-based)  
        is_pro_model: Whether the original request was for Pro model
        
    Returns:
        True if should use Flash model, False if should continue with Pro
    """
    if not is_pro_model:
        return False  # If already using Flash, don't change
    
    return attempt >= FLASH_FALLBACK_THRESHOLD

def get_fallback_model(original_model: str, attempt: int) -> str:
    """
    Get the appropriate model for this attempt based on fallback logic
    
    Args:
        original_model: The originally requested model
        attempt: Current attempt number (0-based)
        
    Returns:
        Model to use for this attempt
    """
    is_pro_model = "pro" in original_model.lower()
    
    if should_use_flash_fallback(attempt, is_pro_model):
        logger.info(f"🔄 SMART FALLBACK: Attempt {attempt + 1} switching from {original_model} to gemini-2.5-flash")
        return "gemini-2.5-flash"
    else:
        return original_model

def enhance_prompt_for_flash_fallback(original_prompt: str, stage_name: str) -> str:
    """
    Enhance prompt when falling back to Flash model to maintain quality
    
    Args:
        original_prompt: The original prompt
        stage_name: Name of the stage (e.g., "Stage 2", "Stage 3", etc.)
        
    Returns:
        Enhanced prompt with additional context for Flash model
    """
    fallback_context = f"""
IMPORTANT: This is a Flash model fallback request for {stage_name}. 
The Pro model encountered issues, so please provide the best possible analysis using Flash capabilities.
Focus on accuracy and completeness despite using a lighter model.

QUALITY REQUIREMENTS:
- Maintain the same JSON structure as expected
- Provide thorough analysis within Flash model capabilities
- If complex reasoning is needed, break it down into simpler steps
- Ensure all required fields are present in the response

ORIGINAL REQUEST:
"""
    
    return fallback_context + original_prompt

def get_configuration_summary() -> dict:
    """Get a summary of current configuration for logging/debugging"""
    return {
        'api_keys_count': len(API_KEYS),
        'api_timeout_seconds': API_TIMEOUT,
        'overall_timeout_seconds': OVERALL_PROCESS_TIMEOUT,
        'max_retries': MAX_RETRIES,
        'base_retry_delay_seconds': BASE_RETRY_DELAY,
        'max_retry_delay_seconds': MAX_RETRY_DELAY,
        'exponential_multiplier': EXPONENTIAL_MULTIPLIER,
        'overload_multiplier': OVERLOAD_MULTIPLIER,
        'pro_model_min_delay_seconds': PRO_MODEL_MIN_DELAY,
        'pro_model_error_delay_seconds': PRO_MODEL_ERROR_DELAY,
        'pro_model_overload_delay_seconds': PRO_MODEL_OVERLOAD_DELAY,
        'flash_fallback_threshold': FLASH_FALLBACK_THRESHOLD,
        'allowed_origins_count': len(ALLOWED_ORIGINS),
        'smart_fallback_enabled': True
    }

# LOG CONFIGURATION ONLY ONCE AT STARTUP
# Only log during main server process, not during uvicorn reloads
if os.getenv("OCR_SERVER_MAIN") == "true":
    config_summary = get_configuration_summary()
    logger.info(f"SMART FALLBACK CONFIG: {config_summary['api_keys_count']} keys | Individual: {config_summary['api_timeout_seconds']}s | Overall: {config_summary['overall_timeout_seconds']}s | Max retries: {config_summary['max_retries']}")
    logger.info(f"REDUCED DELAYS: Base: {config_summary['base_retry_delay_seconds']}s | Max: {config_summary['max_retry_delay_seconds']}s | Multiplier: {config_summary['exponential_multiplier']}x | Overload: {config_summary['overload_multiplier']}x")
    logger.info(f"PRO MODEL SMART PROTECTION: Min: {config_summary['pro_model_min_delay_seconds']}s | Error: {config_summary['pro_model_error_delay_seconds']}s | Overload: {config_summary['pro_model_overload_delay_seconds']}s")
    logger.info(f"FLASH FALLBACK: After attempt {config_summary['flash_fallback_threshold']} | Smart fallback enabled: {config_summary['smart_fallback_enabled']}")
    logger.info(f"CORS: {config_summary['allowed_origins_count']} allowed origins configured")

# LEGACY COMPATIBILITY (deprecated, use the specific getters above)
def get_retry_delay() -> int:
    """Deprecated: Use get_base_retry_delay() instead"""
    logger.warning("get_retry_delay() is deprecated, use get_base_retry_delay() instead")
    return BASE_RETRY_DELAY