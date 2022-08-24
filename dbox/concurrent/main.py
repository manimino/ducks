import pickle
from typing import Any, List, Union, Iterable, Callable, Iterator, Optional, Dict

from readerwriterlock.rwlock import RWLockRead, RWLockWrite, RWLockFair

from dbox.mutable.main import DBox
from contextlib import contextmanager


"""Lock priority options"""
READERS = "readers"
WRITERS = "writers"
FAIR = "fair"


class ConcurrentDBox:
    """Contains a DBox instance and a readerwriterlock. Wraps each DBox method in a read or write lock.

    Args:
        objs: see DBox API
        on: see DBox API
        priority: 'readers', 'writers', or 'fair'. Default 'readers'. Change this according to your usage pattern.
    """

    def __init__(
        self,
        objs: Optional[Iterable[Any]] = None,
        on: Iterable[Union[str, Callable]] = None,
        priority: str = READERS,
    ):
        self.priority = priority
        self.box = DBox(objs, on)
        if priority == READERS:
            self.lock = RWLockRead()
        elif priority == WRITERS:
            self.lock = RWLockWrite()
        elif priority == FAIR:
            self.lock = RWLockFair()
        else:
            raise ValueError(f"priority must be {READERS}, {WRITERS}, or {FAIR}.")
        self._indexes = self.box._indexes  # only used during testing

    @contextmanager
    def read_lock(self):
        """Lock the ConcurrentDBox for reading."""
        with self.lock.gen_rlock():
            yield

    @contextmanager
    def write_lock(self):
        """Lock the ConcurrentDBox for writing.

        When doing many write operations at once, it is more efficient to do::
            with cfb.read_lock():
                for item in items:
                    cfb.box.add(item)  # calls add() on the underlying DBox.

        This performs locking only once, versus calling cfb.add() which locks for each item.
        The same pattern works for update() and remove().
        """
        with self.lock.gen_wlock():
            yield

    def get_values(self, attr: Union[str, Callable]):
        """Get a read lock and perform DBox get_values()."""
        with self.read_lock():
            return self.box.get_values(attr)

    def remove(self, obj: Any):
        """Get a write lock and perform DBox.remove()."""
        with self.write_lock():
            self.box.remove(obj)

    def add(self, obj: Any):
        """Get a write lock and perform DBox.add()."""
        with self.write_lock():
            self.box.add(obj)

    def update(self, obj: Any):
        """Get a write lock and perform DBox.update()."""
        with self.write_lock():
            self.box.update(obj)

    def __len__(self) -> int:
        """Get a read lock and get length of DBox."""
        with self.read_lock():
            return len(self.box)

    def __contains__(self, obj: Any) -> bool:
        """Get a read lock and check if the item is in the DBox."""
        with self.read_lock():
            return obj in self.box

    def __iter__(self) -> Iterator:
        """Get a read lock, make a list of the objects in the DBox, and return an iter to the list."""
        with self.read_lock():
            return iter(list(self.box))

    def __getitem__(self, query: Dict) -> List[Any]:
        """Get a read lock and perform DBox __getitem__."""
        with self.read_lock():
            return self.box[query]


def save(c_box: ConcurrentDBox, filepath: str):
    """Saves a ConcurrentDBox to a pickle file."""
    saved = {
        "objs": list(c_box.box.obj_map.values()),
        "on": list(c_box.box._indexes.keys()),
        "priority": c_box.priority,
    }
    with open(filepath, "wb") as fh:
        pickle.dump(saved, fh)


def load(saved: Dict) -> ConcurrentDBox:
    """Creates a ConcurrentDBox from the pickle file contents."""
    return ConcurrentDBox(saved["objs"], saved["on"], saved["priority"])
