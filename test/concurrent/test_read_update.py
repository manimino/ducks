import threading

from dbox import ConcurrentDBox, DBox
from .concurrent_utils import priority


def worker_read_update(cfb: ConcurrentDBox):
    # this is one concurrency mode -- using the cfb's lock while
    # modifying both the objects and cfb. It's... probably the wrong pattern.
    for obj in cfb:
        with cfb.write_lock():
            obj["x"] += 1
            cfb.box.update(obj)


def test_read_update(priority):
    objs = [{"x": 0} for _ in range(10)]
    cfb = ConcurrentDBox(objs, ["x"], priority=priority)
    threads = []
    for _ in range(5):
        threads.append(threading.Thread(target=worker_read_update, args=(cfb,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for obj in cfb:
        assert obj["x"] == 5


def worker_update(cfb, obj_write_lock):
    with obj_write_lock:
        for obj in cfb:
            obj["x"] += 1
            cfb.update(obj)


def test_two_lock_updating(priority):
    # This is a more sensible locking strategy; objs has its own lock
    # and cfb just worries about itself. Which one is correct kinda depends on how
    # sensitive the user is to stale results. This one would allow stale reads to occur;
    # the other one wouldn't. But this one also allows reads to happen between the writes
    # so that's nice.
    objs = [{"x": 0} for _ in range(10)]
    cfb = ConcurrentDBox(objs, ["x"], priority=priority)
    threads = []
    obj_lock = threading.Lock()
    for _ in range(5):
        threads.append(threading.Thread(target=worker_update, args=(cfb, obj_lock)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for obj in cfb:
        assert obj["x"] == 5
