from typing import Callable, Union, Dict, Any, Iterable, Optional

from cykhash import Int64Set

from hashbox.constants import TUPLE_SIZE_MAX, SET_SIZE_MIN
from hashbox.init_helpers import compute_mutable_dict
from hashbox.utils import get_attribute


class MutableAttrIndex:
    """
    Stores the possible values of this attribute in a collection of buckets.
    Several values may be allocated to the same bucket for space efficiency reasons.
    """

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
        if isinstance(ids, tuple):
            return Int64Set(ids)
        elif isinstance(ids, Int64Set):
            return ids
        else:
            return Int64Set([ids])

    def add(self, ptr: int, obj: Any):
        """Add an object if it has this attribute."""
        val, success = get_attribute(obj, self.attr)
        if not success:
            return
        if val in self.d:
            if isinstance(self.d[val], tuple):
                if len(self.d[val]) == TUPLE_SIZE_MAX:
                    self.d[val] = Int64Set(self.d[val])
                    self.d[val].add(ptr)
                else:
                    self.d[val] = tuple(list(self.d[val]) + [ptr])
            elif isinstance(self.d[val], Int64Set):
                self.d[val].add(ptr)
            else:
                self.d[val] = (self.d[val], ptr)
        else:
            self.d[val] = ptr

    def remove(self, ptr: int, obj: Any):
        """Remove a single object from the index. ptr is already known to be in the index."""
        val, success = get_attribute(obj, self.attr)
        if not success:
            return
        obj_ids = self.d[val]
        if isinstance(obj_ids, tuple) or isinstance(obj_ids, Int64Set):
            if isinstance(obj_ids, tuple):
                self.d[val] = tuple(obj_id for obj_id in obj_ids if obj_id != ptr)
                if len(self.d[val]) == 1:
                    self.d[val] = self.d[val][0]
            else:
                self.d[val].remove(ptr)
                if len(self.d[val]) < SET_SIZE_MIN:
                    self.d[val] = tuple(self.d[val])
        else:
            del self.d[val]

    def get_all_ids(self):
        """Get the ID of every object that has this attribute.
        Called when matching or excluding {attr: hashindex.ANY}."""
        obj_ids = Int64Set()
        for key, val in self.d.items():
            if isinstance(val, tuple):
                obj_ids = obj_ids.union(Int64Set(val))
            elif isinstance(val, Int64Set):
                obj_ids = obj_ids.union(val)
            else:
                obj_ids.add(val)
        return obj_ids

    def __len__(self):
        tot = 0
        for key, val in self.d.items():
            if isinstance(val, tuple) or isinstance(val, Int64Set):
                tot += len(val)
            else:
                tot += 1
        return tot
