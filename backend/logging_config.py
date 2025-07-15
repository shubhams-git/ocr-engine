"""
Centralized logging configuration for OCR Engine API

Provides professional, consistent logging across all modules with:
- Clean, readable formatting without emojis
- Structured log messages for better parsing
- Consistent formatting across all services
- Proper log levels and hierarchy
"""
import logging
import sys
from typing import Optional


class CustomFormatter(logging.Formatter):
    """Custom formatter for clean, professional log output"""
    
    def __init__(self):
        # Clean, professional format
        self.fmt = "%(asctime)s | %(levelname)-5s | %(name)-25s | %(message)s"
        super().__init__(fmt=self.fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        # Truncate long module names for better alignment
        if len(record.name) > 25:
            record.name = "..." + record.name[-22:]
        
        return super().format(record)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up centralized logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Remove all existing handlers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure root logger
    logging.root.setLevel(numeric_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(CustomFormatter())
    
    # Add handler to root logger
    logging.root.addHandler(console_handler)
    
    # Set specific loggers to appropriate levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce HTTP request noise
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent configuration
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Utility functions for common logging patterns
def log_request_start(logger: logging.Logger, endpoint: str, **kwargs) -> None:
    """Log the start of a request with consistent formatting"""
    details = " | ".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    if details:
        logger.info(f"Request started: {endpoint} | {details}")
    else:
        logger.info(f"Request started: {endpoint}")


def log_request_end(logger: logging.Logger, endpoint: str, success: bool, duration: float, **kwargs) -> None:
    """Log the end of a request with consistent formatting"""
    status = "SUCCESS" if success else "FAILED"
    details = " | ".join([f"{k}={v}" for k, v in kwargs.items() if v is not None])
    if details:
        logger.info(f"Request {status}: {endpoint} | Duration: {duration:.2f}s | {details}")
    else:
        logger.info(f"Request {status}: {endpoint} | Duration: {duration:.2f}s")


def log_api_call(logger: logging.Logger, operation: str, model: str, api_key_suffix: str, 
                 duration: Optional[float] = None, success: bool = True, error: Optional[str] = None) -> None:
    """Log API calls with consistent formatting"""
    if success and duration is not None:
        logger.info(f"API call SUCCESS: {operation} | Model: {model} | Key: ...{api_key_suffix} | Duration: {duration:.2f}s")
    elif not success and error:
        duration_str = f" | Duration: {duration:.2f}s" if duration else ""
        logger.error(f"API call FAILED: {operation} | Model: {model} | Key: ...{api_key_suffix}{duration_str} | Error: {error}")
    else:
        logger.info(f"API call STARTED: {operation} | Model: {model} | Key: ...{api_key_suffix}")


def log_file_processing(logger: logging.Logger, action: str, filename: str, 
                       file_size: Optional[int] = None, file_type: Optional[str] = None,
                       duration: Optional[float] = None, success: bool = True) -> None:
    """Log file processing with consistent formatting"""
    details = []
    if file_type:
        details.append(f"Type: {file_type}")
    if file_size is not None:
        size_mb = file_size / (1024 * 1024)
        details.append(f"Size: {size_mb:.2f}MB")
    if duration is not None:
        details.append(f"Duration: {duration:.2f}s")
    
    detail_str = " | " + " | ".join(details) if details else ""
    status = "SUCCESS" if success else "FAILED"
    
    logger.info(f"File {action} {status}: {filename}{detail_str}")


def log_stage_progress(logger: logging.Logger, stage: str, action: str, details: Optional[str] = None) -> None:
    """Log processing stage progress"""
    if details:
        logger.info(f"Stage {stage}: {action} | {details}")
    else:
        logger.info(f"Stage {stage}: {action}")


def log_validation_result(logger: logging.Logger, validation_type: str, passed: bool, 
                         score: Optional[float] = None, issues: Optional[list] = None) -> None:
    """Log validation results"""
    status = "PASSED" if passed else "FAILED"
    details = []
    
    if score is not None:
        details.append(f"Score: {score:.2f}")
    if issues and len(issues) > 0:
        details.append(f"Issues: {len(issues)}")
    
    detail_str = " | " + " | ".join(details) if details else ""
    logger.info(f"Validation {status}: {validation_type}{detail_str}")
    
    # Log specific issues if validation failed
    if not passed and issues:
        for issue in issues[:3]:  # Limit to first 3 issues to avoid spam
            logger.warning(f"Validation issue: {issue}")
        if len(issues) > 3:
            logger.warning(f"Validation has {len(issues) - 3} additional issues") 