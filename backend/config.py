"""
Simple configuration for OCR API with basic API key rotation
Enhanced with cash flow configuration
"""
import os
from logging_config import get_logger

# Set up logger for configuration
logger = get_logger(__name__)

def get_api_keys():
    """Get all available API keys from environment variables"""
    keys = []
    
    # Get the main API key
    main_key = os.getenv("GEMINI_API_KEY")
    if main_key:
        keys.append(main_key)
    
    # Get additional keys (up to 10)
    for i in range(1, 11):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
    
    if not keys:
        raise ValueError("No API keys found. Set GEMINI_API_KEY or GEMINI_API_KEY_1, etc.")
    
    # Use DEBUG level for API key count to reduce startup noise
    logger.debug(f"Loaded {len(keys)} API keys")
    return keys

# Load all available API keys
API_KEYS = get_api_keys()
current_key_index = 0

def get_next_key():
    """Get the next API key in rotation"""
    global current_key_index
    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return key

def get_current_key():
    """Get the current API key without rotating"""
    return API_KEYS[current_key_index]

# API Timeout Configuration
def get_api_timeout():
    """Get API timeout from environment variable or use default"""
    timeout = os.getenv("GEMINI_API_TIMEOUT", "600")
    try:
        return int(timeout)
    except ValueError:
        logger.warning(f"Invalid GEMINI_API_TIMEOUT value: {timeout}, using default 600 seconds")
        return 600

def get_overall_process_timeout():
    """Get overall process timeout from environment variable or use default (10 minutes)"""
    timeout = os.getenv("OVERALL_PROCESS_TIMEOUT", "600")
    try:
        return int(timeout)
    except ValueError:
        logger.warning(f"Invalid OVERALL_PROCESS_TIMEOUT value: {timeout}, using default 600 seconds")
        return 600

def get_max_retries():
    """Get max retries from environment variable or use default"""
    retries = os.getenv("GEMINI_MAX_RETRIES", "2")
    try:
        return int(retries)
    except ValueError:
        logger.warning(f"Invalid GEMINI_MAX_RETRIES value: {retries}, using default 2")
        return 2

def get_retry_delay():
    """Get retry delay from environment variable or use default"""
    delay = os.getenv("GEMINI_RETRY_DELAY", "5")
    try:
        return int(delay)
    except ValueError:
        logger.warning(f"Invalid GEMINI_RETRY_DELAY value: {delay}, using default 5 seconds")
        return 5

# API Configuration
API_TIMEOUT = 1800  # 30 minutes for individual API calls to prevent premature timeouts
OVERALL_PROCESS_TIMEOUT = get_overall_process_timeout()  # 10 minutes for entire process
MAX_RETRIES = get_max_retries()
RETRY_DELAY = get_retry_delay()

# Log configuration only once at startup and only essential info
# Only log during main server process, not during uvicorn reloads
if os.getenv("OCR_SERVER_MAIN") == "true":
    logger.info(f"API Configuration: {len(API_KEYS)} keys | Timeout: {OVERALL_PROCESS_TIMEOUT}s | Retries: {MAX_RETRIES}")

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
] 

# Enhanced Cash Flow Configuration
# Phase 1 default feature flags (authoritative defaults for enhanced cash flow rollout)
_PHASE1_FEATURE_FLAGS = {
    "enhanced_depreciation": True,   # Phase 1 enabled
    "enhanced_validation": False,    # Phase 1 disabled
    "strict_quality_gates": False    # Phase 1 disabled
}

ENHANCED_CASH_FLOW_CONFIG = {
    "depreciation_estimation": {
        "progressive_rates": {
            "small_equipment": {"threshold": 100000, "rate": 0.15, "description": "Tools, small equipment, software"},
            "medium_equipment": {"threshold": 300000, "rate": 0.10, "description": "Vehicles, machinery, computers"},
            "large_equipment": {"threshold": 600000, "rate": 0.07, "description": "Major equipment, plant"},
            "infrastructure": {"threshold": float('inf'), "rate": 0.04, "description": "Buildings, major infrastructure"}
        },
        "min_annual_rate": 0.02,
        "max_annual_rate": 0.25,
        "confidence_thresholds": {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        },
        "fallback_monthly_amount": 1200.0,
        "fallback_annual_rate": 0.05
    },
    "quality_validation": {
        "min_acceptable_global_score": 0.4,
        "base_tolerance_aud": 1000,
        "base_tolerance_pct": 0.02,
        "max_reclass_rate": 0.3,
        "large_variance_threshold": 5000,
        "quality_gate_enabled": True,
        "confidence_multipliers": {
            "high_confidence": 1.0,
            "medium_confidence": 2.0,
            "low_confidence": 3.0
        }
    },
    # Align existing feature flags to Phase 1 defaults while preserving only the three keys required by scope
    "feature_flags": {
        "enhanced_depreciation": _PHASE1_FEATURE_FLAGS["enhanced_depreciation"],
        "enhanced_validation": _PHASE1_FEATURE_FLAGS["enhanced_validation"],
        "strict_quality_gates": _PHASE1_FEATURE_FLAGS["strict_quality_gates"],
        # Added logging flag to prevent KeyError in BusinessAnalysisService
        "enhanced_logging": False
    },
    "monitoring": {
        "track_quality_improvements": True,
        "log_depreciation_analysis": True,
        "alert_on_quality_degradation": True,
        "performance_benchmarking": True
    },
    "classification_rules": {
        "owner_drawings": {
            "min_fcf_threshold": -5000,
            "ni_fcf_ratio_threshold": 0.5
        },
        "data_quality_issues": {
            "confidence_threshold": 0.6,
            "variance_range": [1000, 5000]
        },
        "working_capital_anomalies": {
            "wc_variance_ratio": 0.8
        }
    },
    "australian_business_standards": {
        "financial_year": "july_to_june",
        "depreciation_methods": [
            "diminishing_value",
            "prime_cost",
            "simplified_depreciation"
        ],
        "small_business_thresholds": {
            "turnover_threshold": 10000000,
            "instant_asset_writeoff": 20000
        }
    }
}

# Backward-compatible boolean validation retained but renamed internally
def _validate_enhanced_config_boolean() -> bool:
    """Validate the enhanced configuration (legacy boolean-based validator)."""
    try:
        required_sections = ["depreciation_estimation", "quality_validation", "feature_flags"]
        for section in required_sections:
            if section not in ENHANCED_CASH_FLOW_CONFIG:
                raise ValueError(f"Missing required config section: {section}")

        rates = ENHANCED_CASH_FLOW_CONFIG["depreciation_estimation"]["progressive_rates"]
        for category, info in rates.items():
            if "threshold" not in info or "rate" not in info:
                raise ValueError(f"Invalid depreciation rate config for {category}")

        validation_config = ENHANCED_CASH_FLOW_CONFIG["quality_validation"]
        if validation_config["base_tolerance_aud"] <= 0:
            raise ValueError("Base tolerance AUD must be positive")

        if not (0 < validation_config["base_tolerance_pct"] < 1):
            raise ValueError("Base tolerance percentage must be between 0 and 1")

        logger.debug("Enhanced configuration validation passed")
        return True
    except Exception as e:
        logger.error(f"Enhanced configuration validation failed: {str(e)}")
        return False


# Lightweight dict-level validator for enhanced feature flags (non-throwing)
def validate_enhanced_config(cfg: dict) -> dict:
    """
    Validates enhanced cash flow config and applies safe defaults.
    Returns a sanitized config dict without raising exceptions.

    Behavior:
    - Ensures cfg is a dict and contains a 'feature_flags' dict.
    - Ensures the three Phase 1 keys exist and are booleans.
    - Any missing or invalid entries are replaced with Phase 1 defaults.
    - Extra keys are preserved untouched to avoid breaking existing consumers.
    """
    try:
        sanitized = {} if not isinstance(cfg, dict) else dict(cfg)  # shallow copy
        ff = sanitized.get("feature_flags")
        if not isinstance(ff, dict):
            ff = {}
        ff_out = dict(ff)  # preserve extra keys

        # Ensure Phase 1 keys exist and are booleans; otherwise set defaults
        for k, v in _PHASE1_FEATURE_FLAGS.items():
            cur = ff_out.get(k, v)
            # Coerce to bool only if value is truthy/falsey but not bool, else use default
            if isinstance(cur, bool):
                ff_out[k] = cur
            else:
                try:
                    ff_out[k] = bool(cur)
                except Exception:
                    ff_out[k] = v

        sanitized["feature_flags"] = ff_out
        return sanitized
    except Exception:
        # On any unexpected issue, return just Phase 1 defaults to be safe
        return {"feature_flags": dict(_PHASE1_FEATURE_FLAGS)}

# Validate configuration on import
if os.getenv("OCR_SERVER_MAIN") == "true":
    if _validate_enhanced_config_boolean():
        logger.info("Enhanced Cash Flow Configuration loaded successfully")
        logger.info(f"🔧 Feature flags enabled: {sum(1 for k, v in ENHANCED_CASH_FLOW_CONFIG['feature_flags'].items() if v)}/{len(ENHANCED_CASH_FLOW_CONFIG['feature_flags'])}")
    else:
        logger.warning("Enhanced configuration validation failed - using defaults")