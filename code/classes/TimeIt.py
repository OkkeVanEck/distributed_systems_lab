import logging
import time
from functools import wraps

def timeit(func=None, timer=None, counter=None):
    def actual_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            end = time.time()
            if timer:
                timer[f"{f.__name__}"] += round(end - start, 2)
                if counter:
                    counter[f"{f.__name__}"] += 1
            else:
                logging.info(f"timer {func.__name__} {round(end - start, 2)}s")
            return result
        return wrapper
    if func:
        return actual_decorator(func)
    return actual_decorator