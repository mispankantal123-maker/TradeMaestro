"""
Utility Functions Module
Common utility functions and helper methods.
"""

import gc
import os
import sys
import time
import datetime
import threading
from typing import List, Optional, Dict, Any, Union
import json

from config import *


def cleanup_resources() -> None:
    """
    Comprehensive resource cleanup utility.
    
    This function helps prevent memory leaks by explicitly cleaning up
    large data structures and forcing garbage collection.
    """
    try:
        # Force garbage collection
        gc.collect()
        
        # Clear any large global variables if they exist
        global_vars_to_clear = ['large_dataframes', 'cached_data', 'temp_storage']
        for var_name in global_vars_to_clear:
            if var_name in globals():
                try:
                    globals()[var_name].clear()
                except:
                    pass
        
        print("🧹 Memory cleanup completed")
        
    except Exception as e:
        print(f"⚠️ Memory cleanup error: {str(e)}")


def validate_numeric_input(value: Union[str, float, int], 
                          min_val: float = 0.0, 
                          max_val: Optional[float] = None) -> float:
    """
    Validate and convert numeric input with proper error handling.
    
    Args:
        value: Input value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value (optional)
        
    Returns:
        float: Validated numeric value
        
    Raises:
        ValueError: If validation fails
    """
    try:
        if isinstance(value, str):
            numeric_value = float(value.strip())
        else:
            numeric_value = float(value)
            
        if numeric_value < min_val:
            raise ValueError(f"Value {numeric_value} is below minimum {min_val}")
            
        if max_val is not None and numeric_value > max_val:
            raise ValueError(f"Value {numeric_value} exceeds maximum {max_val}")
            
        return numeric_value
        
    except (ValueError, TypeError, AttributeError) as e:
        raise ValueError(f"Invalid numeric input '{value}': {str(e)}")


def validate_string_input(value: str, 
                         allowed_values: Optional[List[str]] = None,
                         min_length: int = 1,
                         max_length: Optional[int] = None) -> str:
    """
    Validate string input with specific criteria.
    
    Args:
        value: String value to validate
        allowed_values: List of allowed values (optional)
        min_length: Minimum string length
        max_length: Maximum string length (optional)
        
    Returns:
        str: Validated string
        
    Raises:
        ValueError: If validation fails
    """
    try:
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
            
        clean_value = value.strip()
        
        if len(clean_value) < min_length:
            raise ValueError(f"String too short (minimum {min_length} characters)")
            
        if max_length is not None and len(clean_value) > max_length:
            raise ValueError(f"String too long (maximum {max_length} characters)")
            
        if allowed_values and clean_value.upper() not in [v.upper() for v in allowed_values]:
            raise ValueError(f"Value '{clean_value}' not in allowed values: {allowed_values}")
            
        return clean_value
        
    except AttributeError as e:
        raise ValueError(f"Invalid string input: {str(e)}")


def format_currency(amount: float, currency: str = "USD", decimals: int = 2) -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Amount to format
        currency: Currency code
        decimals: Number of decimal places
        
    Returns:
        str: Formatted currency string
    """
    try:
        return f"{amount:,.{decimals}f} {currency}"
    except Exception as e:
        return f"{amount} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage value for display.
    
    Args:
        value: Percentage value (e.g., 0.15 for 15%)
        decimals: Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    try:
        return f"{value * 100:.{decimals}f}%"
    except Exception as e:
        return f"{value}%"


def format_pips(value: float, decimals: int = 1) -> str:
    """
    Format pip value for display.
    
    Args:
        value: Pip value
        decimals: Number of decimal places
        
    Returns:
        str: Formatted pip string
    """
    try:
        return f"{value:.{decimals}f} pips"
    except Exception as e:
        return f"{value} pips"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers with default for division by zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if denominator is zero
        
    Returns:
        float: Division result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


def timestamp_to_datetime(timestamp: float) -> datetime.datetime:
    """
    Convert timestamp to datetime object.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        datetime: Datetime object
    """
    try:
        return datetime.datetime.fromtimestamp(timestamp)
    except Exception as e:
        return datetime.datetime.now()


def datetime_to_string(dt: datetime.datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Convert datetime to formatted string.
    
    Args:
        dt: Datetime object
        format_string: Format string
        
    Returns:
        str: Formatted datetime string
    """
    try:
        return dt.strftime(format_string)
    except Exception as e:
        return str(dt)


def ensure_directory(directory_path: str) -> bool:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        bool: True if directory exists or was created
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            return True
        return True
    except Exception as e:
        print(f"❌ Failed to create directory {directory_path}: {str(e)}")
        return False


def save_json_file(data: Dict[str, Any], filepath: str) -> bool:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: File path
        
    Returns:
        bool: True if saved successfully
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"❌ Failed to save JSON file {filepath}: {str(e)}")
        return False


def load_json_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load data from JSON file.
    
    Args:
        filepath: File path
        
    Returns:
        Dict or None: Loaded data or None if failed
    """
    try:
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON file {filepath}: {str(e)}")
        return None


def retry_operation(operation, max_attempts: int = 3, delay: float = 1.0):
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation: Function to retry
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts
        
    Returns:
        Operation result or None if all attempts fail
    """
    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"❌ Operation failed after {max_attempts} attempts: {str(e)}")
                return None
            else:
                print(f"⚠️ Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
    
    return None


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for diagnostics.
    
    Returns:
        Dict with system information
    """
    try:
        import platform
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version()
        }
    except Exception as e:
        return {"error": f"Failed to get system info: {str(e)}"}


def calculate_time_difference(start_time: datetime.datetime, 
                            end_time: datetime.datetime) -> Dict[str, Any]:
    """
    Calculate time difference with detailed breakdown.
    
    Args:
        start_time: Start datetime
        end_time: End datetime
        
    Returns:
        Dict with time difference breakdown
    """
    try:
        diff = end_time - start_time
        total_seconds = int(diff.total_seconds())
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return {
            "total_seconds": total_seconds,
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "formatted": f"{days}d {hours}h {minutes}m {seconds}s"
        }
    except Exception as e:
        return {"error": f"Failed to calculate time difference: {str(e)}"}


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated string
    """
    try:
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    except Exception as e:
        return str(text)


def get_file_size(filepath: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        filepath: Path to file
        
    Returns:
        int: File size in bytes, 0 if file doesn't exist
    """
    try:
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0
    except Exception as e:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    except Exception as e:
        return f"{size_bytes} B"


def is_trading_time() -> bool:
    """
    Check if current time is within general trading hours.
    
    Returns:
        bool: True if within trading hours
    """
    try:
        utc_now = datetime.datetime.utcnow()
        day_of_week = utc_now.weekday()  # 0=Monday, 6=Sunday
        
        # Forex market is closed on weekends
        if day_of_week == 5:  # Saturday
            # Market closes Friday 22:00 UTC
            if utc_now.hour >= 22:
                return False
        elif day_of_week == 6:  # Sunday
            # Market opens Sunday 22:00 UTC
            if utc_now.hour < 22:
                return False
        
        return True
    except Exception as e:
        return True  # Default to allow trading if check fails


def create_backup_filename(original_filename: str) -> str:
    """
    Create backup filename with timestamp.
    
    Args:
        original_filename: Original filename
        
    Returns:
        str: Backup filename with timestamp
    """
    try:
        name, ext = os.path.splitext(original_filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_backup_{timestamp}{ext}"
    except Exception as e:
        return f"{original_filename}_backup"


class ThreadSafeCounter:
    """Thread-safe counter utility."""
    
    def __init__(self, initial_value: int = 0):
        """Initialize counter."""
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self, amount: int = 1) -> int:
        """Increment counter and return new value."""
        with self._lock:
            self._value += amount
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        """Decrement counter and return new value."""
        with self._lock:
            self._value -= amount
            return self._value
    
    def get_value(self) -> int:
        """Get current counter value."""
        with self._lock:
            return self._value
    
    def reset(self) -> None:
        """Reset counter to zero."""
        with self._lock:
            self._value = 0


class RateLimiter:
    """Simple rate limiter utility."""
    
    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self._lock = threading.Lock()
    
    def can_proceed(self) -> bool:
        """
        Check if operation can proceed within rate limit.
        
        Returns:
            bool: True if within rate limit
        """
        with self._lock:
            current_time = time.time()
            
            # Remove old calls outside time window
            self.calls = [call_time for call_time in self.calls 
                         if current_time - call_time < self.time_window]
            
            # Check if we can make another call
            if len(self.calls) < self.max_calls:
                self.calls.append(current_time)
                return True
            
            return False
    
    def time_until_next_call(self) -> float:
        """
        Get time until next call is allowed.
        
        Returns:
            float: Seconds until next call allowed
        """
        with self._lock:
            if len(self.calls) < self.max_calls:
                return 0.0
            
            current_time = time.time()
            oldest_call = min(self.calls)
            return max(0.0, self.time_window - (current_time - oldest_call))
