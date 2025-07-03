"""
Configuration settings for the OCR Engine Backend
"""
import os
import random
import logging
from typing import List, Dict

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.info("📂 Loaded environment variables from .env file")
except ImportError:
    # dotenv not installed, environment variables should be set manually
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        # Server settings
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
        
        # CORS settings
        self.FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
        self.ALLOWED_ORIGINS: List[str] = [
            "http://localhost:5173", 
            "http://127.0.0.1:5173",
            "http://localhost:3000"  # Alternative frontend port
        ]
        
        # File upload settings
        self.MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
        self.ALLOWED_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".pdf"]
        self.UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
        
        # API settings
        self.API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
        self.RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "100"))  # requests per minute

# Gemini API Keys with rotation support
class GeminiAPIManager:
    """Manages multiple Gemini API keys with rotation"""
    
    def __init__(self):
        # Load API keys from environment variables
        self.api_keys = []
        
        # Try to load up to 10 API keys from environment
        for i in range(1, 11):
            key_env_name = f"GEMINI_API_KEY_{i}"
            api_key = os.getenv(key_env_name)
            
            if api_key:
                self.api_keys.append({
                    "name": f"Backable_{i}",
                    "key": api_key.strip()
                })
        
        # Fallback: if no keys found in environment, show error
        if not self.api_keys:
            logger.error("❌ No Gemini API keys found in environment variables!")
            logger.error("Please set GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc. in your .env file")
            # Add a dummy key to prevent crashes during development
            self.api_keys = [{"name": "MISSING", "key": "PLEASE_SET_ENV_VARIABLES"}]
        self.current_index = 0
        self.failed_keys = set()
        logger.info(f"🔑 Initialized API key manager with {len(self.api_keys)} keys")
    
    def get_next_api_key(self) -> Dict[str, str]:
        """Get the next API key in rotation"""
        available_keys = [key for i, key in enumerate(self.api_keys) if i not in self.failed_keys]
        
        if not available_keys:
            # Reset failed keys if all have failed
            logger.warning("⚠️ All API keys failed, resetting rotation")
            self.failed_keys.clear()
            available_keys = self.api_keys
        
        # Use round-robin rotation
        if self.current_index >= len(available_keys):
            self.current_index = 0
            
        selected_key = available_keys[self.current_index]
        self.current_index += 1
        
        logger.info(f"🔄 Using API key: {selected_key['name']}")
        return selected_key
    
    def get_random_api_key(self) -> Dict[str, str]:
        """Get a random API key (alternative to round-robin)"""
        available_keys = [key for i, key in enumerate(self.api_keys) if i not in self.failed_keys]
        
        if not available_keys:
            logger.warning("⚠️ All API keys failed, resetting rotation")
            self.failed_keys.clear()
            available_keys = self.api_keys
        
        selected_key = random.choice(available_keys)
        logger.info(f"🎲 Using random API key: {selected_key['name']}")
        return selected_key
    
    def mark_key_failed(self, key_name: str):
        """Mark an API key as failed"""
        for i, key in enumerate(self.api_keys):
            if key['name'] == key_name:
                self.failed_keys.add(i)
                logger.error(f"❌ Marked API key as failed: {key_name}")
                break
    
    def mark_key_success(self, key_name: str):
        """Mark an API key as successful (remove from failed list)"""
        for i, key in enumerate(self.api_keys):
            if key['name'] == key_name:
                if i in self.failed_keys:
                    self.failed_keys.remove(i)
                    logger.info(f"✅ API key back online: {key_name}")
                break
    
    def get_key_stats(self) -> Dict:
        """Get statistics about API key usage"""
        total_keys = len(self.api_keys)
        failed_keys = len(self.failed_keys)
        active_keys = total_keys - failed_keys
        
        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "failed_keys": failed_keys,
            "success_rate": f"{(active_keys/total_keys)*100:.1f}%"
        }

# Global instances
settings = Settings()
api_manager = GeminiAPIManager()

# Available Gemini models
GEMINI_MODELS = [
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "provider": "google",
        "description": "Most powerful thinking model with maximum response accuracy"
    },
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "provider": "google", 
        "description": "Best price-performance model with well-rounded capabilities"
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "provider": "google",
        "description": "Previous generation pro model with excellent capabilities"
    },
    {
        "id": "gemini-1.5-flash",
        "name": "Gemini 1.5 Flash",
        "provider": "google",
        "description": "Fast and versatile performance across diverse tasks"
    }
]

# Logging configuration
def setup_logging():
    """Set up enhanced logging for the application"""
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # Custom formatter for better readability
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Update console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Apply to root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    logger.info("🚀 Logging system initialized")

# Initialize logging
setup_logging() 