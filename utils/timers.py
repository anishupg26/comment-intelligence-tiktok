import time
from contextlib import contextmanager


@contextmanager
def timed():
    start = time.time()
    yield lambda: time.time() - start
