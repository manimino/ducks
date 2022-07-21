from bisect import bisect_right

import numpy as np

from hashindex.init_helpers import BucketPlan
from hashindex.constants import SIZE_THRESH
from hashindex.frozen_buckets import (
    FDictBucket,
    FHashBucket,
    ArrayPair,
    empty_array_pair,
)
from typing import List, Union, Callable


class FrozenFieldIndex:
    def __init__(self, field: Union[str, Callable], bucket_plans: List[BucketPlan]):
        self.buckets = []
        self.bucket_min_hashes = []
        self.field = field
        for bp in bucket_plans:
            if (
                len(bp.distinct_hash_counts) == 1
                and bp.distinct_hash_counts > SIZE_THRESH
            ):
                b = FDictBucket(bp, self.field)
            else:
                b = FHashBucket(bp, self.field)
            self.bucket_min_hashes.append(bp.distinct_hashes[0])
            self.buckets.append(b)

    def get(self, val) -> ArrayPair:
        val_hash = hash(val)
        # Note: this line assumes self.bucket_min_hashes is sorted, which it is because bucket_plans is sorted.
        list_idx = bisect_right(self.bucket_min_hashes, val_hash) - 1
        b = self.buckets[list_idx]
        return b.get(val)

    def get_obj_ids(self, val) -> np.ndarray:
        return self.get(val).id_arr

    def get_all(self) -> ArrayPair:
        arrs = empty_array_pair()
        for b in self.buckets:
            arrs.apply_union(b.get_all())
        return arrs

    def __iter__(self):
        return FrozenFieldIndexIterator(self)

    def __len__(self):
        return sum(len(b) for b in self.buckets)


class FrozenFieldIndexIterator:

    def __init__(self, ffi: FrozenFieldIndex):
        self.buckets = ffi.buckets
        self.i = 0
        self.bucket_iter = iter(self.buckets[self.i])

    def __next__(self):
        while True:
            got_obj = False
            try:
                obj = next(self.bucket_iter)
                got_obj = True
            except StopIteration:
                self.i += 1
                if self.i == len(self.buckets):
                    raise StopIteration
                self.bucket_iter = iter(self.buckets[self.i])
            if got_obj:
                return obj
