import functools
import time
from typing import Callable, Any
from src.core.logger import setup_logger

logger = setup_logger(__name__)


def timing_decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.debug(f"{func.__name__} completed in {elapsed_time:.2f}ms")
        return result
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                        time.sleep(delay * (attempt + 1))
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts")
            
            raise last_exception
        return wrapper
    return decorator


def validate_transaction_data(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if 'transaction' in kwargs:
            transaction = kwargs['transaction']
            
            if hasattr(transaction, 'amount') and transaction.amount < 0:
                raise ValueError("Transaction amount cannot be negative")
            
            if hasattr(transaction, 'timestamp') and transaction.timestamp is None:
                raise ValueError("Transaction timestamp is required")
        
        return func(*args, **kwargs)
    return wrapper
