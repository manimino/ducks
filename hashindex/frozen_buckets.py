import numpy as np
import sortednp as snp
from dataclasses import dataclass
from collections import Counter
from hashindex.init_helpers import BucketPlan
from hashindex.utils import get_field
from typing import Callable, Union


@dataclass
class ArrayPair:
    id_arr: np.ndarray
    obj_arr: np.ndarray

    def intersect(self, other):
        pass

    def union(self, other):
        pass

    def difference(self, other):
        pass


def make_array_pair(obj_arr: np.ndarray):
    """Finds obj_ids and sorts obj_arr by the ids. Returns an ArrayPair."""
    obj_ids = np.empty_like(obj_arr, dtype='int64')
    for i, obj in enumerate(obj_arr):
        obj_ids[i] = id(obj)
    sort_order = np.argsort(obj_ids)
    return ArrayPair(
        id_arr=obj_ids[sort_order],
        obj_arr=obj_arr[sort_order]
    )


class FHashBucket:
    def __init__(self, bp: BucketPlan):
        self.array_pair = make_array_pair(bp.obj_arr)


class FDictBucket:
    def __init__(self, bp: BucketPlan, field: Union[str, Callable]):
        first = bp.val_arr[0]  # assumption: bp will never be empty (true as long as bucket size limit >= 1)
        if all(val == first for val in bp.val_arr):
            # In the overwhelming majority of cases, val will be unique.
            self.d = {first: make_array_pair(bp.obj_arr)}
        else:
            # Building a dict requires hashing every value, so there's some time cost here (~1s per 1M items).
            # Maybe worse since, as we know, the value hashes collide.
            d_idx = dict()
            for i, val in enumerate(bp.val_arr):
                if val not in self.d:
                    d_idx[val] = []
                d_idx[val].append(i)
            for val in self.d_idx:
                self.d[val] = bp.obj_arr[d_idx[val]]
