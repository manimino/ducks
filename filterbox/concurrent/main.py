from typing import Any, List, Union, Iterable, Callable, Iterator

from readerwriterlock.rwlock import RWLockRead, RWLockWrite, RWLockFair

from filterbox.mutable.main import FilterBox
from contextlib import contextmanager


"""Lock priority options"""
READERS = 'readers'
WRITERS = 'writers'
FAIR = 'fair'


class ConcurrentFilterBox:
    def __init__(self, objs, on=None, priority: str = 'readers'):
        """Wraps each FilterBox method in the appropriate lock.
        Prioritizes readers by default; writes will wait until no readers are active.

        Args:
            objs: see FilterBox API
            on: see FilterBox API
            priority: 'readers', 'writers', or 'fair'. Change this according to your usage pattern.
        """
        self.box = FilterBox(objs, on)
        if priority == READERS:
            self.lock = RWLockRead()
        elif priority == WRITERS:
            self.lock = RWLockWrite()
        elif priority == FAIR:
            self.lock = RWLockFair()
        else:
            raise ValueError(f"priority must be {READERS}, {WRITERS}, or {FAIR}.")
        self._indices = self.box._indices  # pass-through, used during testing

    @contextmanager
    def read_lock(self):
        with self.lock.gen_rlock():
            yield

    @contextmanager
    def write_lock(self):
        with self.lock.gen_wlock():
            yield

    def find(self, match=None, exclude=None) -> List[Any]:
        with self.read_lock():
            return self.box.find(match, exclude)

    def get_values(self, attr: Union[str, Callable]):
        with self.read_lock():
            return self.box.get_values(attr)

    def remove(self, obj: Any):
        with self.write_lock():
            self.box.remove(obj)

    def add(self, obj: Any):
        with self.write_lock():
            self.box.add(obj)

    def update(self, obj: Any):
        with self.write_lock():
            self.box.update(obj)

    def __len__(self) -> int:
        with self.read_lock():
            return len(self.box)

    def __contains__(self, item) -> bool:
        with self.read_lock():
            return item in self.box

    def __iter__(self) -> Iterator:
        """Returning an iter to a collection that other threads are modifying is a bad idea.
        Instead this makes a list of the currently contained objects and returns an iterator on that."""
        with self.read_lock():
            return iter(list(self.box))
