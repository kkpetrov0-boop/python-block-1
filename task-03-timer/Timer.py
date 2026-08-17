import logging
from contextlib import contextmanager
import time

timerlevel = 0
logger = logging.getLogger(__name__)

class ClassTimer:
    def __init__(self, block_marker: str):
        self.block_marker = block_marker
        self._enter = False

    def __enter__(self):
        if self._enter:
            raise SyntaxError("Cannot insert class specimen into itself")
        global timerlevel
        timerlevel += 1
        self.start = time.perf_counter()
        self._enter = True
        return self._enter

    def __exit__(self, exc_type, exc, tb):
        self._enter = False
        global timerlevel
        self.stop = time.perf_counter()
        logger.info(f"  " * (timerlevel - 1) + self.block_marker + f" time: {self.stop-self.start}")
        timerlevel -= 1
        
@contextmanager
def timer_2(block_marker):
    try:
        global timerlevel
        timerlevel += 1
        start = time.perf_counter()
        yield

    finally:
        stop = time.perf_counter()
        logger.info(f"{(timerlevel - 1) * "  "}{block_marker} time: {stop - start}")
        timerlevel -= 1


def main():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(message)s -%(asctime)s - [%(levelname)s]",
        datefmt="%Y-%m-%d, %H-%M-%S"
        )
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    
    with ClassTimer("Outer Class") as some:
        with ClassTimer("Mid Class") as something:
            with ClassTimer("Inner Class") as pppp:
                print("This is inside Class")
         #   raise TypeError

    with timer_2("Outer contextmanager") as abc:
        with timer_2("Mid contextmanager") as dbm:
            with timer_2("Inner contextmanager") as inner:
                #raise TypeError
                print("This is inside context manager")


if __name__ == "__main__":
    main()