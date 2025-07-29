"""
Optimized logging configuration for OCR Engine API
Reduces log clutter while maintaining essential development information
"""
import logging
import sys
import os
from typing import Optional, Any

# Color codes for console output
class LogColors:
    GREY = '\x1b[38;20m'
    YELLOW = '\x1b[33;20m'
    RED = '\x1b[31;20m'
    BOLD_RED = '\x1b[31;1m'
    GREEN = '\x1b[32;20m'
    BLUE = '\x1b[34;20m'
    RESET = '\x1b[0m'

class ColoredFormatter(logging.Formatter):
    """Enhanced formatter with colors and reduced verbosity"""
    
    FORMATS = {
        logging.DEBUG: LogColors.GREY + "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s" + LogColors.RESET,
        logging.INFO: LogColors.GREEN + "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s" + LogColors.RESET,
        logging.WARNING: LogColors.YELLOW + "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s" + LogColors.RESET,
        logging.ERROR: LogColors.RED + "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s" + LogColors.RESET,
        logging.CRITICAL: LogColors.BOLD_RED + "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s" + LogColors.RESET,
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

def setup_logging():
    """Set up optimized logging configuration"""
    # Get environment log level (default to INFO for development)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
        datefmt='%H:%M:%S',
        handlers=[]
    )
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    
    # Get root logger and clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Reduce verbosity for external libraries
    _configure_external_loggers()
    
    # Only show startup message once
    if os.getenv("OCR_SERVER_MAIN") == "true":
        logger = logging.getLogger(__name__)
        logger.info(f"🚀 Optimized logging initialized | Level: {log_level}")

def _configure_external_loggers():
    """Configure external library loggers to reduce noise"""
    external_loggers = [
        'uvicorn.access',
        'uvicorn.error', 
        'httpx',
        'watchfiles.main',
        'google_genai.models',
        'google.generativeai'
    ]
    
    for logger_name in external_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger with optimized configuration"""
    return logging.getLogger(name)

# Simplified logging helper functions with reduced verbosity
def log_request_start(logger: logging.Logger, request_type: str, **kwargs):
    """Log request start with minimal info"""
    details = []
    if 'files' in kwargs:
        details.append(f"files={kwargs['files']}")
    if 'model' in kwargs:
        details.append(f"model={kwargs['model']}")
    if 'total_size_mb' in kwargs:
        details.append(f"size={kwargs['total_size_mb']}MB")
    
    details_str = " | ".join(details)
    logger.info(f"🚀 {request_type} started | {details_str}")

def log_request_end(logger: logging.Logger, request_type: str, success: bool, duration: float, **kwargs):
    """Log request completion with essential info"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    logger.info(f"{status} {request_type} | Duration: {duration:.1f}s")

def log_stage_progress(logger: logging.Logger, stage: str, status: str, details: str = ""):
    """Log stage progress with reduced verbosity"""
    if status == "STARTED":
        emoji = "🔄"
    elif status == "COMPLETED":
        emoji = "✅"
    elif "FAIL" in status.upper() or "ERROR" in status.upper():
        emoji = "❌"
    else:
        # For descriptive statuses like "Enhancing analysis", default to the success icon
        # as it's an informational log about an action, not a failure.
        emoji = "✅"
    
    base_msg = f"{emoji} Stage {stage} {status.lower()}"
    if details:
        logger.info(f"{base_msg} | {details}")
    else:
        logger.info(base_msg)

def log_file_processing(logger: logging.Logger, action: str, filename: str, 
                       file_size: Optional[int] = None, success: bool = True):
    """Log file processing with minimal details"""
    if action == "received" and file_size:
        size_mb = file_size / (1024 * 1024)
        logger.debug(f"📁 File {action}: {filename} | {size_mb:.2f}MB")
    elif action == "read" and success:
        logger.debug(f"📖 File read: {filename}")
    else:
        logger.debug(f"📁 File {action}: {filename}")

def log_validation_result(logger: logging.Logger, validation_type: str, 
                         passed: bool, details: Optional[str] = None):
    """Log validation results concisely"""
    status = "✅ PASS" if passed else "❌ FAIL"
    msg = f"{status} {validation_type}"
    if details and not passed:  # Only show details for failures
        msg += f" | {details}"
    logger.info(msg)

def log_api_call(logger: logging.Logger, operation: str, model: str, 
                duration: Optional[float] = None, attempt: int = 1, success: bool = True):
    """Log API calls with reduced verbosity"""
    if success and duration:
        logger.debug(f"🔗 API call: {operation} | Model: {model} | {duration:.1f}s | Attempt: {attempt}")
    elif not success:
        logger.warning(f"⚠️ API call failed: {operation} | Model: {model} | Attempt: {attempt}")
    else:
        logger.debug(f"🔗 API call started: {operation} | Model: {model}")

# Development mode helpers
def log_semaphore_operation(logger: logging.Logger, operation: str, stage: str, available: int):
    """Log semaphore operations only in debug mode"""
    logger.debug(f"🔒 {operation} semaphore | Stage: {stage} | Available: {available}")

def log_rate_limit_operation(logger: logging.Logger, operation: str, delay: float, reason: str = ""):
    """Log rate limiting with reduced noise"""
    if delay > 10:  # Only log significant delays
        logger.info(f"⏱️ Rate limit: {operation} | Delay: {delay:.1f}s | {reason}")
    else:
        logger.debug(f"⏱️ Rate limit: {operation} | {delay:.1f}s")

def log_model_operation(logger: logging.Logger, model: str, operation: str, 
                       duration: Optional[float] = None, success: bool = True):
    """Log model operations with essential info only"""
    if success and duration:
        if duration > 60:  # Only log long operations at INFO level
            logger.info(f"🤖 {model} {operation} | {duration:.1f}s")
        else:
            logger.debug(f"🤖 {model} {operation} | {duration:.1f}s")
    elif not success:
        logger.warning(f"⚠️ {model} {operation} failed")

def log_error_with_context(logger: logging.Logger, error: Exception, context: str = ""):
    """Log errors with minimal context"""
    error_msg = str(error)
    if "503" in error_msg or "overload" in error_msg.lower():
        logger.warning(f"🚨 API overload | {context} | {error_msg}")
    else:
        logger.error(f"❌ Error | {context} | {error_msg}")

def log_config_summary(logger: logging.Logger, config: dict):
    """Log configuration summary at startup only"""
    if os.getenv("OCR_SERVER_MAIN") == "true":
        key_configs = [
            f"keys={config.get('api_keys_count', 0)}",
            f"timeout={config.get('overall_timeout_seconds', 0)}s",
            f"retries={config.get('max_retries', 0)}"
        ]
        logger.info(f"⚙️ Config loaded | {' | '.join(key_configs)}")