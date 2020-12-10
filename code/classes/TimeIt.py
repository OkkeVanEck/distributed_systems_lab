import logging
import time
from functools import wraps

def timeit(func=None, timer=None):
    def actual_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            end = time.time()
            if timer:
                timer[f"{f.__name__}"] += round(end - start, 2)
            else:
                logging.info(f"{func.__name__} takes {round(end - start, 2)}s")
            return result
        return wrapper
    if func:
        return actual_decorator(func)
    return actual_decorator