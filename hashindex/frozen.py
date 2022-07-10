from typing import Optional, Any, Dict, Union, Callable, Iterable

import numpy as np
import sortednp as snp
from hashindex.constants import SIZE_THRESH
from hashindex.exceptions import MissingIndexError
from hashindex.frozen_field import FrozenFieldIndex
from hashindex.init_helpers import compute_buckets
from hashindex.utils import int_arr


class FrozenHashIndex:
    def __init__(self,
                 objs: Optional[Iterable[Any]] = None,
                 on: Iterable[Union[str, Callable]] = None
                 ):
        """
        TODO: we may not actually need these arrays, since they can be read out of any field index.
        Consider removing.
        """
        self.id_arr = np.array([id(obj) for obj in objs], dtype="uint64")
        self.obj_arr = np.array(objs, dtype="O")
        self.on = on
        self.indices = {}
        for field in on:
            plan = compute_buckets(objs, field, SIZE_THRESH)
            self.indices[field] = FrozenFieldIndex(plan)

    def find(self,
             match: Optional[Dict[Union[str, Callable], Any]] = None,
             exclude: Optional[Dict[Union[str, Callable], Any]] = None,
             ) -> np.ndarray:
        pass

    def _find_obj_id(self, ptr):
        """Use binary search to look up the position of an obj id in the sorted numpy array."""
        i = self.id_arr.searchsorted(ptr)
        if i == len(self.id_arr):
            # happens when index is empty, or the ptr is bigger than any obj ptr we have
            return -1
        # searchsorted tells us the first index <= target, check for ==
        if self.id_arr[i] == ptr:
            return i
        return -1

    def __contains__(self, obj):
        return self._find_obj_id(id(obj)) != -1

    def __iter__(self):
        return iter(self.objects)
