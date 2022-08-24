from array import array
from typing import Callable, Union, Dict, Any, Iterable, Optional, Hashable, Set

from cykhash import Int64Set

from filterbox.constants import ANY, ARR_TYPE, ARRAY_SIZE_MAX, SET_SIZE_MIN
from filterbox.utils import get_attribute
from filterbox.btree import BTree


class MutableAttrIndex:
    """Stores data and handles requests that are relevant to a single attribute of a FilterBox."""

    def __init__(
        self, attr: Union[Callable, str], objs: Optional[Iterable[Any]] = None,
    ):
        self.attr = attr
        self.none_ids = Int64Set()  # Stores object IDs for the attribute value None
        self.tree = BTree()  # Stores object IDs for all other values
        self.n_obj_ids = 0
        if objs:
            for obj in objs:
                self.add(id(obj), obj)

    def add(self, ptr: int, obj: Any):
        """Add an object if it has this attribute."""
        val, success = get_attribute(obj, self.attr)
        if not success:
            return
        self._add_val(ptr, val)
        self.n_obj_ids += 1

    def get_obj_ids(self, val: Any) -> Int64Set:
        """Get the object IDs associated with this value as an Int64Set."""
        if val is ANY:
            return self.get_all_ids()
        if val is None:
            return self.none_ids
        ids = self.tree.get(val, Int64Set())
        if type(ids) is array:
            return Int64Set(ids)
        elif type(ids) is Int64Set:
            return ids
        else:
            return Int64Set([ids])

    def remove(self, ptr: int, obj: Any):
        """Remove a single object from the index. ptr is already known to be in the FilterBox.
        Runs in O(1) if obj has this attr and the value of the attr hasn't changed. O(n_keys) otherwise."""
        removed = False
        val, success = get_attribute(obj, self.attr)
        if success:
            removed = self._try_remove(ptr, val)
        if not removed:
            # do O(n) search
            for val in list(self.tree.keys()):
                removed = self._try_remove(ptr, val)
                if removed:
                    break

    def get_all_ids(self) -> Int64Set:
        """Get the ID of every object that has this attribute.
        Called when matching or excluding ``{attr: hashindex.ANY}``."""
        obj_ids = Int64Set(self.none_ids)
        for key, val in self.tree.items():
            self._add_val_to_set(val, obj_ids)
        return obj_ids

    def get_values(self) -> Set:
        """Get unique values we have objects for."""
        vals = set(self.tree.keys())
        if len(self.none_ids):
            vals.add(None)
        return vals

    def get_ids_by_range(self, expr: Dict[str, Any]):
        """Get object IDs based on less than / greater than some value"""
        obj_ids = Int64Set()
        vals = self.tree.get_range_expr(expr)
        for val in vals:
            self._add_val_to_set(val, obj_ids)
        return obj_ids

    def _add_val(self, ptr, val):
        if val is None:
            self.none_ids.add(ptr)
        elif val in self.tree:
            obj_ids = self.tree[val]
            if type(obj_ids) is Int64Set:
                self.tree[val].add(ptr)
            elif type(obj_ids) is array:
                if len(obj_ids) == ARRAY_SIZE_MAX:
                    # upgrade array -> set
                    obj_ids = Int64Set(obj_ids)
                    obj_ids.add(ptr)
                    self.tree[val] = obj_ids
                else:
                    obj_ids.append(ptr)
            else:
                # obj_ids was an int, now we have two. upgrade int -> array
                self.tree[val] = array(ARR_TYPE, [obj_ids, ptr])
        else:
            # new val, add the int
            self.tree[val] = ptr

    @staticmethod
    def _add_val_to_set(val: Any, obj_ids: Int64Set):
        """We need to do this a lot"""
        if type(val) in [array, Int64Set]:
            for v in val:
                obj_ids.add(v)
        else:
            obj_ids.add(val)

    def _try_remove(self, ptr: int, val: Hashable) -> bool:
        """Try to remove the object from self.tree[val]. Return True on success, False otherwise."""
        # handle None
        if val is None and ptr in self.none_ids:
            self.none_ids.remove(ptr)
            self.n_obj_ids -= 1
            return True

        # first, check that the ptr is in here
        if val not in self.tree:
            return False
        if type(self.tree[val]) in [array, Int64Set]:
            if ptr not in self.tree[val]:
                return False
        else:
            if self.tree[val] != ptr:
                return False

        # must be in the tree
        obj_ids = self.tree[val]
        if type(self.tree[val]) in [array, Int64Set]:
            self.tree[val].remove(ptr)
            if type(obj_ids) is array:
                if len(self.tree[val]) == 1:
                    # downgrade array -> int
                    self.tree[val] = self.tree[val][0]
            else:
                if len(self.tree[val]) < SET_SIZE_MIN:
                    # downgrade set -> array
                    self.tree[val] = array(ARR_TYPE, list(self.tree[val]))
        else:
            # downgrade int -> nothing
            del self.tree[val]
        self.n_obj_ids -= 1
        return True

    def __len__(self):
        return self.n_obj_ids
