#!/usr/bin/env python3
"""
Centralized error handling and logging for Gap Hunter Bot
Provides consistent error handling patterns across the application
"""

import logging
import traceback
import functools
from typing import Any, Callable, Optional, Dict, List
import requests
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gap_hunter')

class GapHunterError(Exception):
    """Base exception for Gap Hunter Bot"""
    pass

class APIError(GapHunterError):
    """API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, api_name: str = "Unknown"):
        self.status_code = status_code
        self.api_name = api_name
        super().__init__(f"{api_name} API Error: {message}")

class ValidationError(GapHunterError):
    """Input validation errors"""
    pass

class ConfigurationError(GapHunterError):
    """Configuration-related errors"""
    pass

def handle_api_errors(api_name: str, required_keys: Optional[List[str]] = None):
    """
    Decorator for handling API errors consistently
    
    Args:
        api_name: Name of the API for error messages
        required_keys: List of required environment variables
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Check required environment variables
                if required_keys:
                    import os
                    missing_keys = [key for key in required_keys if not os.environ.get(key)]
                    if missing_keys:
                        logger.warning(f"{api_name}: Missing required keys: {missing_keys}")
                        return []
                
                return func(*args, **kwargs)
                
            except requests.exceptions.Timeout:
                logger.warning(f"{api_name}: Request timeout")
                return []
            except requests.exceptions.ConnectionError:
                logger.warning(f"{api_name}: Connection error")
                return []
            except requests.exceptions.HTTPError as e:
                logger.warning(f"{api_name}: HTTP error {e.response.status_code}")
                return []
            except Exception as e:
                logger.error(f"{api_name}: Unexpected error: {str(e)}")
                return []
                
        return wrapper
    return decorator

def validate_input(min_length: int = 1, max_length: int = 1000, required: bool = True):
    """
    Decorator for input validation
    
    Args:
        min_length: Minimum string length
        max_length: Maximum string length
        required: Whether the input is required
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate first string argument (usually query)
            if args and len(args) > 1:
                query = args[1]  # Skip self
                
                if required and (not query or not str(query).strip()):
                    raise ValidationError("Input is required but was empty")
                
                if query:
                    query_str = str(query).strip()
                    if len(query_str) < min_length:
                        raise ValidationError(f"Input too short (minimum {min_length} characters)")
                    if len(query_str) > max_length:
                        logger.warning(f"Input truncated from {len(query_str)} to {max_length} characters")
                        # Modify args to include truncated query
                        args = list(args)
                        args[1] = query_str[:max_length]
                        args = tuple(args)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for retrying failed operations
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for delay on each retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {str(e)}")
            
            # If all retries failed, raise the last exception
            raise last_exception
            
        return wrapper
    return decorator

def safe_execute(func: Callable, default_return: Any = None, log_errors: bool = True) -> Any:
    """
    Safely execute a function and return default value on error
    
    Args:
        func: Function to execute
        default_return: Value to return on error
        log_errors: Whether to log errors
    
    Returns:
        Function result or default_return on error
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"Error in {func.__name__}: {str(e)}")
        return default_return

def log_performance(func: Callable) -> Callable:
    """Decorator to log function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper

def handle_streamlit_errors(func: Callable) -> Callable:
    """Decorator for handling errors in Streamlit context"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            try:
                import streamlit as st
                st.error(f"❌ Input Error: {str(e)}")
                st.info("💡 Please check your input and try again")
            except ImportError:
                print(f"❌ Input Error: {str(e)}")
            return None
        except APIError as e:
            try:
                import streamlit as st
                st.error(f"❌ {str(e)}")
                st.info("💡 Please check your API configuration and try again")
            except ImportError:
                print(f"❌ {str(e)}")
            return None
        except Exception as e:
            try:
                import streamlit as st
                st.error(f"❌ Unexpected error: {str(e)}")
                st.info("💡 Please try again or contact support")
            except ImportError:
                print(f"❌ Unexpected error: {str(e)}")
            logger.error(f"Unexpected error in {func.__name__}: {traceback.format_exc()}")
            return None
    return wrapper

def create_error_response(error_message: str, error_type: str = "error") -> Dict[str, str]:
    """
    Create standardized error response
    
    Args:
        error_message: Human-readable error message
        error_type: Type of error (error, warning, info)
    
    Returns:
        Standardized error response dictionary
    """
    return {
        "error": error_message,
        "type": error_type,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# Utility functions for common error scenarios
def check_api_keys(required_keys: List[str]) -> List[str]:
    """Check for missing API keys and return list of missing ones"""
    import os
    return [key for key in required_keys if not os.environ.get(key)]

def is_valid_query(query: str, min_length: int = 3, max_length: int = 200) -> tuple[bool, str]:
    """
    Validate search query
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    query = query.strip()
    if len(query) < min_length:
        return False, f"Query too short (minimum {min_length} characters)"
    
    if len(query) > max_length:
        return False, f"Query too long (maximum {max_length} characters)"
    
    return True, ""

def format_api_error(response: requests.Response, api_name: str) -> str:
    """Format API error message based on status code"""
    status_code = response.status_code
    
    if status_code == 401:
        return f"{api_name}: Invalid or missing API key"
    elif status_code == 403:
        return f"{api_name}: Access forbidden - check API key permissions"
    elif status_code == 429:
        return f"{api_name}: Rate limit exceeded - please wait before retrying"
    elif status_code == 500:
        return f"{api_name}: Server error - please try again later"
    elif status_code == 503:
        return f"{api_name}: Service unavailable - please try again later"
    else:
        return f"{api_name}: HTTP {status_code} error"
