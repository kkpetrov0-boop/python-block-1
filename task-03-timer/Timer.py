import logging
from contextlib import contextmanager
import time

timerlevel = 0
logger = logging.getLogger(__name__)

class ClassTimer:
    def __init__(self, block_marker: str):
        self.block_marker = block_marker
        self._entered = False

    def __enter__(self):
        if self._entered:
            raise RuntimeError(f"Timer '{self.block_marker}' is already active")
        global timerlevel
        timerlevel += 1
        self.start = time.perf_counter()
        self._entered = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self._entered = False
        global timerlevel
        stop = time.perf_counter()
        logger.info(f"  " * (timerlevel - 1) + self.block_marker + f" time: {(stop-self.start):.6f}")
        timerlevel -= 1
        
@contextmanager
def timer_2(block_marker):
    global timerlevel
    timerlevel += 1
    start = time.perf_counter()
    try:
        yield

    finally:
        stop = time.perf_counter()
        logger.info(f"{(timerlevel - 1) * "  "}{block_marker} time: {(stop - start):.6f}")
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

    
    with ClassTimer("Outer Class") as outer:
        with ClassTimer("Mid Class") as mid:
            with ClassTimer("Inner Class") as inner:
                print("This is inside Class")
         #   raise TypeError

    with timer_2("Outer contextmanager") as outer:
        with timer_2("Mid contextmanager") as mid:
            with timer_2("Inner contextmanager") as inner:
                #raise TypeError
                print("This is inside context manager")

    with timer_2("Outer contextmanager") as outer:
            with ClassTimer("Mid Class") as mid:
                    #raise TypeError
                    print("This is inside context manager/Class")
    


if __name__ == "__main__":
    main()