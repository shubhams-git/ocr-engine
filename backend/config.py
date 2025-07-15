"""
Simple configuration for OCR API with basic API key rotation
"""
import os

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
    
    print(f"Loaded {len(keys)} API keys")
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
        print(f"Invalid GEMINI_API_TIMEOUT value: {timeout}, using default 600 seconds")
        return 600

def get_overall_process_timeout():
    """Get overall process timeout from environment variable or use default (10 minutes)"""
    timeout = os.getenv("OVERALL_PROCESS_TIMEOUT", "600")
    try:
        return int(timeout)
    except ValueError:
        print(f"Invalid OVERALL_PROCESS_TIMEOUT value: {timeout}, using default 600 seconds")
        return 600

def get_max_retries():
    """Get max retries from environment variable or use default"""
    retries = os.getenv("GEMINI_MAX_RETRIES", "2")
    try:
        return int(retries)
    except ValueError:
        print(f"Invalid GEMINI_MAX_RETRIES value: {retries}, using default 2")
        return 2

def get_retry_delay():
    """Get retry delay from environment variable or use default"""
    delay = os.getenv("GEMINI_RETRY_DELAY", "5")
    try:
        return int(delay)
    except ValueError:
        print(f"Invalid GEMINI_RETRY_DELAY value: {delay}, using default 5 seconds")
        return 5

# API Configuration
API_TIMEOUT = 1800  # 30 minutes for individual API calls to prevent premature timeouts
OVERALL_PROCESS_TIMEOUT = get_overall_process_timeout()  # 10 minutes for entire process
MAX_RETRIES = get_max_retries()
RETRY_DELAY = get_retry_delay()

print(f"API Configuration | Individual API Timeout: {API_TIMEOUT}s | Overall Process Timeout: {OVERALL_PROCESS_TIMEOUT}s | Max Retries: {MAX_RETRIES} | Retry Delay: {RETRY_DELAY}s")

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
] 