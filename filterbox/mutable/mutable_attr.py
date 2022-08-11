from array import array
from typing import Callable, Union, Dict, Any, Iterable, Optional, Hashable, Set

from cykhash import Int64Set

from filterbox.constants import ARR_TYPE, ARRAY_SIZE_MAX, SET_SIZE_MIN
from filterbox.init_helpers import compute_mutable_dict
from filterbox.utils import get_attribute


class MutableAttrIndex:
    """Stores data and handles requests that are relevant to a single attribute of a FilterBox."""

    def __init__(
        self,
        attr: Union[Callable, str],
        obj_map: Dict[int, Any],
        objs: Optional[Iterable[Any]] = None,
    ):
        self.attr = attr
        self.obj_map = obj_map
        if objs:
            self.d = compute_mutable_dict(objs, attr)
        else:
            self.d = dict()

    def get_obj_ids(self, val: Any) -> Int64Set:
        """Get the object IDs associated with this value as an Int64Set."""
        ids = self.d.get(val, Int64Set())
        if type(ids) is array:
            return Int64Set(ids)
        elif type(ids) is Int64Set:
            return ids
        else:
            return Int64Set([ids])

    def add(self, ptr: int, obj: Any):
        """Add an object if it has this attribute."""
        val, success = get_attribute(obj, self.attr)
        if not success:
            return
        if val in self.d:
            if type(self.d[val]) is Int64Set:
                self.d[val].add(ptr)
            elif type(self.d[val]) is array:
                if len(self.d[val]) == ARRAY_SIZE_MAX:
                    # upgrade array -> set
                    self.d[val] = Int64Set(self.d[val])
                    self.d[val].add(ptr)
                else:
                    self.d[val].append(ptr)
            else:
                # upgrade int -> array
                self.d[val] = array(ARR_TYPE, [self.d[val], ptr])
        else:
            self.d[val] = ptr

    def _try_remove(self, ptr: int, val: Hashable) -> bool:
        """Try to remove the object from self.d[val]. Return True on success, False otherwise."""
        # first, check that the ptr is in here
        if val not in self.d:
            return False
        if type(self.d[val]) in [array, Int64Set]:
            if ptr not in self.d[val]:
                return False
        else:
            if self.d[val] != ptr:
                return False

        # OK, it's in here; do removal
        obj_ids = self.d[val]
        if type(self.d[val]) in [array, Int64Set]:
            self.d[val].remove(ptr)
            if type(obj_ids) is array:
                if len(self.d[val]) == 1:
                    # downgrade array -> int
                    self.d[val] = self.d[val][0]
            else:
                if len(self.d[val]) < SET_SIZE_MIN:
                    # downgrade set -> array
                    self.d[val] = array(ARR_TYPE, list(self.d[val]))
        else:
            # downgrade int -> nothing
            del self.d[val]
        return True

    def remove(self, ptr: int, obj: Any):
        """Remove a single object from the index. ptr is already known to be in the FilterBox.
        Runs in O(1) if obj has this attr and the value of the attr hasn't changed. O(n_keys) otherwise."""
        removed = False
        val, success = get_attribute(obj, self.attr)
        if success:
            removed = self._try_remove(ptr, val)
        if not removed:
            # do O(n) search
            for val in list(self.d.keys()):
                self._try_remove(ptr, val)

    def get_all_ids(self) -> Int64Set:
        """Get the ID of every object that has this attribute.
        Called when matching or excluding ``{attr: hashindex.ANY}``."""
        obj_ids = Int64Set()
        for key, val in self.d.items():
            if type(val) is array:
                obj_ids = obj_ids.union(Int64Set(val))
            elif type(val) is Int64Set:
                obj_ids = obj_ids.union(val)
            else:
                obj_ids.add(val)
        return obj_ids

    def get_values(self) -> Set:
        """Get unique values we have objects for."""
        return set(self.d.keys())

    def __len__(self):
        tot = 0
        for key, val in self.d.items():
            if type(val) in [array, Int64Set]:
                tot += len(val)
            else:
                tot += 1
        return tot
