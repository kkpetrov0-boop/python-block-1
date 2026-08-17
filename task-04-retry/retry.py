import time
import random
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry(attempts=5, base_delay=0.1, max_delay=30.0,
       jitter=True, exceptions=(ConnectionError,),
       on_retry=None, sleep=time.sleep):
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            #print(range(attempts))
            for n in range(attempts):

                try:
                    result = func(*args, **kwargs)
                except exceptions as e:
                    logger.error("%s failed: %s", func.__name__, e)
                    if n == attempts - 1:
                        raise
                    delay = base_delay * 2**n
                    delay = min(delay, max_delay)
                    if jitter:
                        delay = random.uniform(delay, delay * 2)
                    if on_retry:
                        on_retry(n+1, e, delay)
                    sleep(delay)
                else:
                    return result  
        return wrapper
    return decorator
    
def retry_cb(attempt, exception, delay):
    logger.debug(f"Attempt: {attempt}, exception: {type(exception).__name__}, delay: {delay:.3f}")



@retry(attempts=5, base_delay=0.1, max_delay=30.0,
       jitter=False, exceptions=(ConnectionError,),
       on_retry=retry_cb, sleep=print)
def test_func():
    return True

@retry(attempts=5, base_delay=0.1, max_delay=30.0,
       jitter=True, exceptions=(ConnectionError,),
       on_retry=retry_cb, sleep=print)
def test_func2():
    #raise ValueError
    raise ConnectionError("broker unreachable")
    return False

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s, [%(levelname)s] %(message)s",
                        datefmt="%H:%M:%S")
    print(test_func.__name__)
    print(test_func2.__name__)
    test_func()
    test_func2()



if __name__ == "__main__":
    main()