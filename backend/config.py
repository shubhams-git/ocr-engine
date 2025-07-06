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

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
] 