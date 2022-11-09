import threading
import time
from typing import Any
from typing import List

import pytest
from ducks import ConcurrentDex

from .concurrent_utils import priority
from .concurrent_utils import slow_wrapper


def worker_add_remove(objs: List[Any], box: ConcurrentDex, end_full=True):
    """The worker thread adds and removes each element of objs."""
    for i in range(10):
        for obj in objs:
            box.add(obj)
        for obj in objs:
            try:
                box.remove(obj)
            except KeyError:
                # the other worker may have removed it already; that's OK.
                pass
    if end_full:
        for obj in objs:
            box.add(obj)


@pytest.mark.parametrize(
    "end_full, expected_len", [(True, 10), (False, 0),],
)
def test_add_remove(priority, end_full, expected_len):
    objs = [{"x": i % 2} for i in range(10)]

    box = ConcurrentDex(objs, ["x"], priority=priority)
    # box = Dex(objs, ['x'])  # <--- use this instead, and you will observe frequent failures on this test.

    # Patch indexes 'add' to add a small delay, forcing race conditions to occur more often
    box._indexes["x"].add = slow_wrapper(box._indexes["x"].add)

    duration = 0.2
    t0 = time.time()
    while time.time() - t0 < duration:
        t1 = threading.Thread(
            target=worker_add_remove, args=[objs, box], kwargs={"end_full": end_full}
        )
        t2 = threading.Thread(
            target=worker_add_remove, args=[objs, box], kwargs={"end_full": end_full}
        )
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        assert len(box) == expected_len
        assert len(box._indexes["x"]) == expected_len  # fails on Dex
