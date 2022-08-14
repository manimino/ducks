from array import array
from typing import Callable, Union, Dict, Any, Iterable, Optional, Hashable, Set

from cykhash import Int64Set

from filterbox.constants import ARR_TYPE, ARRAY_SIZE_MAX, SET_SIZE_MIN
from filterbox.utils import get_attribute
from BTrees.OOBTree import OOBTree


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
        self.d = OOBTree()
        self.n_objs = 0  # len() is terribly slow on BTree, so we maintain it ourselves.
        if objs:
            for obj in objs:
                self.add(id(obj), obj)

    def get_index_type(self):
        if type(self.d) is dict:
            return "hash"
        else:
            return "tree"

    def add(self, ptr: int, obj: Any):
        """Add an object if it has this attribute."""
        val, success = get_attribute(obj, self.attr)
        if not success:
            return
        try:
            # if this is the first val, check if it's a comparable type.
            if self.n_objs == 0:
                _ = val > val  # triggers a TypeError if not comparable
            self._add_val(ptr, val)
        except TypeError:
            # someone threw in a type we can't compare. Downgrade to dict and retry the add.
            self.d = dict(self.d)
            self._add_val(ptr, val)
        self.n_objs += 1

    def _add_val(self, ptr, val):
        if val in self.d:
            obj_ids = self.d[val]
            if type(obj_ids) is Int64Set:
                self.d[val].add(ptr)
            elif type(obj_ids) is array:
                if len(obj_ids) == ARRAY_SIZE_MAX:
                    # upgrade array -> set
                    obj_ids = Int64Set(obj_ids)
                    obj_ids.add(ptr)
                    self.d[val] = obj_ids
                else:
                    obj_ids.append(ptr)
            else:
                # obj_ids was an int, now we have two. upgrade int -> array
                self.d[val] = array(ARR_TYPE, [obj_ids, ptr])
        else:
            # new val, add the int
            self.d[val] = ptr

    def get_obj_ids(self, val: Any) -> Int64Set:
        """Get the object IDs associated with this value as an Int64Set."""
        ids = self.d.get(val, Int64Set())
        if type(ids) is array:
            return Int64Set(ids)
        elif type(ids) is Int64Set:
            return ids
        else:
            return Int64Set([ids])

    @staticmethod
    def _add_val_to_set(val: Any, obj_ids: Int64Set):
        """We need to do this a lot"""
        if type(val) in [array, Int64Set]:
            for v in val:
                obj_ids.add(v)
        else:
            obj_ids.add(val)

    def get_ids_by_range(self, lo, hi, include_lo=False, include_hi=False) -> Int64Set:
        """Get the object IDs associated with this value range as an Int64Set. Only usable when self.d is a tree."""
        if type(self.d) is OOBTree:
            obj_ids = Int64Set()
            if lo is None:
                lo = min(self.d)
                include_lo = True
            if hi is None:
                hi = max(self.d)
                include_hi = True
            # get values >= lo and <= hi
            for val in self.d.values(lo, hi):
                self._add_val_to_set(val, obj_ids)
            # if < or >, we need to remove the end points manually
            but_not_these = Int64Set()
            if not include_lo and lo in self.d:
                self._add_val_to_set(self.d[lo], but_not_these)
            if not include_hi and hi in self.d:
                self._add_val_to_set(self.d[hi], but_not_these)
            return obj_ids.difference(but_not_these)
        else:
            raise ValueError("Not a BTree - you have to get one at a time")

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
                removed = self._try_remove(ptr, val)
                if removed:
                    break
        if removed:
            self.n_objs -= 1

    def get_all_ids(self) -> Int64Set:
        """Get the ID of every object that has this attribute.
        Called when matching or excluding ``{attr: hashindex.ANY}``."""
        obj_ids = Int64Set()
        for key, val in self.d.items():
            self._add_val_to_set(val, obj_ids)
        return obj_ids

    def get_values(self) -> Set:
        """Get unique values we have objects for."""
        return set(self.d.keys())

    def __len__(self):
        return self.n_objs
