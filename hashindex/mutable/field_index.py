from typing import Callable, Union, Dict, Any, List, Iterable, Optional

from cykhash import Int64Set

from hashindex.constants import SIZE_THRESH, HASH_MIN, HASH_MAX
from hashindex.init_helpers import compute_mutable_dict
from hashindex.utils import get_field

import numpy as np


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

    def add(self, obj_id, obj):
        val = get_field(obj, self.field)
        val_hash = hash(val)
        k = self.mbm.get_bucket_key_for(val_hash)
        self.mbm[k].add(val, obj_id)

    def remove(self, obj_id, obj):
        """
        Remove a single object from the index.

        If a bucket ever gets empty, remove it.
        """
        val = get_field(obj, self.field)
        val_hash = hash(val)
        k = self.mbm.get_bucket_key_for(val_hash)
        if len(self.mbm[k]) == 0:
            self.mbm.remove_bucket(k)
