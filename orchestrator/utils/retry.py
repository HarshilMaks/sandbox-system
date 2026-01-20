"""Retry logic with exponential backoff."""
import asyncio
import functools
from typing import Callable, Any
import random


def with_retry(
    max_attempts: int = 3,
    exponential_backoff: bool = True,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        exponential_backoff: Use exponential backoff
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        # Calculate delay
                        if exponential_backoff:
                            delay = min(
                                base_delay * (2 ** attempt) + random.uniform(0, 1),
                                max_delay
                            )
                        else:
                            delay = base_delay
                        
                        await asyncio.sleep(delay)
            
            # All attempts failed
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        if exponential_backoff:
                            delay = min(
                                base_delay * (2 ** attempt) + random.uniform(0, 1),
                                max_delay
                            )
                        else:
                            delay = base_delay
                        
                        import time
                        time.sleep(delay)
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
