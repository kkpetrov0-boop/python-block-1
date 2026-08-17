from retry import retry
import logging
import time
import inspect
import math

BASE = 0.1
MAX = 30.0

start = time.perf_counter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s, [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")

delays= []

def accumulate(arg):
    delays.append(arg)

retries = []
def retry_cb(attempt, exception, delay):
    one_log = {"Attempt": attempt, "exception": type(exception).__name__, "delay": delay}
    retries.append(one_log)

@retry(base_delay=BASE, max_delay=MAX, jitter=False, sleep = accumulate, on_retry=retry_cb)
def test_no_jitter():
    '''Переподключение'''
    raise ConnectionError

try:
    test_no_jitter()
    assert False, "ConnectionError не поднялся"
except ConnectionError:
    pass

assert len(delays) == 4
for i in range(len(delays)):
    assert math.isclose(delays[i], BASE * 2**(i)), "Wrong delay order"
    assert retries[i] == {"Attempt": (i+1), "exception": "ConnectionError", "delay": BASE * 2**(i)}, f"Wrong call_back {retries[i]} {i}"
delays.clear()

assert test_no_jitter.__name__ == "test_no_jitter", "Wrong name"
assert test_no_jitter.__doc__ == "Переподключение", "Wrong __doc__"

@retry(base_delay=BASE, max_delay=MAX, sleep = accumulate)
def test_with_jitter():
    raise ConnectionError

try:
    test_with_jitter()
    assert False, "ConnectionError не поднялся"
except ConnectionError:
    pass

assert len(delays) == 4
for i in range(len(delays)):
    delay = BASE * 2**(i)
    delay = min(delay, MAX)
    assert delay <= delays[i] < delay * 2, "Wrong delay with jitter"

delays.clear()

@retry(base_delay=BASE, max_delay=MAX, sleep = accumulate)
def test_ValueError():
    raise ValueError("ValueError")

try:
    test_ValueError()
    assert False, "ValueError"
except ValueError:
    pass

assert not delays, "Was working dispite ValueError"

delays.clear()

@retry(base_delay=BASE, max_delay=0.5, jitter=False, sleep = accumulate)
def test_max_delay():
    raise ConnectionError

try:
    test_max_delay()
    assert False, "ConnectionError не поднялся"
except ConnectionError:
    pass

assert delays == [0.1, 0.2, 0.4, 0.5], "Max delay exceed the limit"
delays.clear()



assert inspect.signature(retry).parameters["base_delay"].default == BASE, "wrong base delay"
assert inspect.signature(retry).parameters["max_delay"].default == MAX, "wrong max delay"

time_result = time.perf_counter() - start
assert time_result < 0.1, f"Too much time for test {time_result}"