from typing import Callable, Union, Dict, Any, Iterable, Optional

from cykhash import Int64Set

from hashindex.constants import SIZE_THRESH
from hashindex.init_helpers import compute_mutable_dict
from hashindex.utils import get_field


class MutableFieldIndex:
    """
    Stores the possible values of this field in a collection of buckets.
    Several values may be allocated to the same bucket for space efficiency reasons.
    """

    def __init__(
        self,
        field: Union[Callable, str],
        obj_map: Dict[int, Any],
        objs: Optional[Iterable[Any]] = None,
    ):
        self.field = field
        self.obj_map = obj_map
        if objs:
            self.d = compute_mutable_dict(objs, field)
        else:
            self.d = dict()

    def get_obj_ids(self, val):
        val_hash = hash(val)
        k = self.mbm.get_bucket_key_for(val_hash)
        bucket = self.mbm[k]
        return bucket.get_matching_ids(val)

    def add(self, ptr, obj):
        val = get_field(obj, self.field)
        if val in self.d:
            if len(self.d[val]) == SIZE_THRESH:
                self.d[val] = Int64Set(self.d[val])
                self.d[val].add(ptr)
            elif isinstance(self.d[val], tuple):
                self.d[val] = tuple(list(self.d[val]) + [ptr])
            else:
                self.d[val].add(ptr)
        else:
            self.d[val] = tuple(val)

    def remove(self, ptr, obj):
        """
        Remove a single object from the index.

        If a val slot ever gets empty, remove it.
        """
        val = get_field(obj, self.field)
        obj_ids = self.d[val]
        if ptr in obj_ids:
            if isinstance(obj_ids, tuple):
                self.d[val] = tuple(obj_id for obj_id in obj_ids if obj_id != ptr)
            else:
                self.d[val].remove(ptr)
            if len(self.d[val]) == 0:
                del self.d[val]
            # TODO set -> tuple change
