from retry import retry
import logging
import time
import inspect
import math
import pytest

BASE = 0.1
MAX = 30.0



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s, [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")

delays = []
retries = []

@pytest.fixture
def cleanup():
    yield
    delays.clear()
    retries.clear()

def accumulate(arg):
    delays.append(arg)


def retry_cb(attempt, exception, delay):
    one_log = {"Attempt": attempt, "exception": type(exception).__name__, "delay": delay}
    retries.append(one_log)

@retry(base_delay=BASE, max_delay=MAX, jitter=False, sleep = accumulate, on_retry=retry_cb)
def no_jitter():
    '''Переподключение'''
    raise ConnectionError

def test_no_jitter(cleanup):
    with pytest.raises(ConnectionError):
        no_jitter()
    assert len(delays) == 4
    for i in range(len(delays)):
        assert math.isclose(delays[i], BASE * 2**(i))
        assert retries[i] == {"Attempt": (i+1), "exception": "ConnectionError", "delay": BASE * 2**(i)}
    assert no_jitter.__doc__ == "Переподключение", "Wrong __doc__"


@retry(base_delay=BASE, max_delay=MAX, sleep = accumulate)
def with_jitter():
    raise ConnectionError

def test_with_jitter(cleanup):
    with pytest.raises(ConnectionError):
        with_jitter()
    assert len(delays) == 4
    for i in range(len(delays)):
        delay = BASE * 2**(i)
        delay = min(delay, MAX)
        assert delay <= delays[i] < delay * 2



@retry(base_delay=BASE, max_delay=MAX, sleep = accumulate)
def value_error():
    raise ValueError("ValueError")

def test_value_error(cleanup):
    with pytest.raises(ValueError):
        value_error()
    assert not delays


@retry(base_delay=BASE, max_delay=0.5, jitter=False, sleep = accumulate)
def max_delay():
    raise ConnectionError

def test_max_delay(cleanup):
    with pytest.raises(ConnectionError):
        max_delay()
    assert delays == [0.1, 0.2, 0.4, 0.5], "Max delay exceed the limit"



def test_defaults():
    assert inspect.signature(retry).parameters["base_delay"].default == BASE, "wrong base delay"
    assert inspect.signature(retry).parameters["max_delay"].default == MAX, "wrong max delay"

