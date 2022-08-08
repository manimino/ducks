import threading

from filterbox import ConcurrentFilterBox, FilterBox
from .concurrent_utils import priority


def worker_read_update(cfb: ConcurrentFilterBox):
    for obj in cfb:
        with cfb.write_lock():
            obj['x'] += 1
            cfb.box.update(obj)


def test_read_update(priority):
    objs = [{'x': 0} for _ in range(10)]
    cfb = ConcurrentFilterBox(objs, ['x'], priority=priority)
    threads = []
    for _ in range(5):
        threads.append(threading.Thread(target=worker_read_update, args=(cfb,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for obj in cfb:
        assert obj['x'] == 5
