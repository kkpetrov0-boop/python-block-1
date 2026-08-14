from contextlib import contextmanager
import logging
class Test:
    val = 0
    def __init__(self):
        print("create")

    def __enter__(self):
        print("This is enter")
        Test.val += 1
        return Test.val

    def __exit__(self, exc_type, exc, tb):
        print("this is exit")
        Test.val -= 1
        print(f"{exc_type=} {exc=} {tb=}")
        return True

@contextmanager
def test_decorator():
    try:
        print("This is enter decorator")
        yield 50
    except:
        print("this is except")
    finally:
        print("this is finally")

test_class = Test()
test_class2 = Test()
print(type(test_class))
with test_class as something:
    print(something)
    with test_class2 as something:
        print(something)
    raise TypeError


with test_decorator() as something:
    print(something)


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)



logger.critical("Error")

