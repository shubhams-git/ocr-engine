"""
Simple configuration for OCR API
"""
import os
import random
from typing import List

# Load API keys from environment variables
API_KEYS = []
for i in range(1, 11):  # Support up to 10 API keys
    key = os.getenv(f"GEMINI_API_KEY_{i}")
    if key:
        API_KEYS.append(key.strip())

# If no keys found, check for single key
if not API_KEYS:
    single_key = os.getenv("GEMINI_API_KEY")
    if single_key:
        API_KEYS.append(single_key.strip())

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Simple API key rotation
current_key_index = 0

def get_api_key() -> str:
    """Get next API key in rotation"""
    global current_key_index
    
    if not API_KEYS:
        raise ValueError("No Gemini API keys found. Please set GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.")
    
    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    
    return key

def get_random_api_key() -> str:
    """Get random API key"""
    if not API_KEYS:
        raise ValueError("No Gemini API keys found")
    
    return random.choice(API_KEYS)

def get_api_key_count() -> int:
    """Get number of available API keys"""
    return len(API_KEYS) 