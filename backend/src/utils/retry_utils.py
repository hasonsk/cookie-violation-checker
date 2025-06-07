import asyncio
from functools import wraps
from loguru import logger

def retry(max_attempts: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0, exceptions=(Exception,)):
    """
    A decorator to retry a function call with exponential backoff.

    Args:
        max_attempts (int): Maximum number of attempts.
        initial_delay (float): Initial delay in seconds before the first retry.
        backoff_factor (float): Factor by which the delay increases each time.
        exceptions (tuple): A tuple of exceptions to catch and retry on.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}")
                    if attempt < max_attempts:
                        logger.info(f"Retrying {func.__name__} in {delay:.2f} seconds...")
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}.")
                        raise
        return wrapper
    return decorator
