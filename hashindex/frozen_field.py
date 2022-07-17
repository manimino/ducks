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

    def get_objs(self, val) -> np.ndarray:
        return self.get(val).obj_arr

    def get_all(self) -> ArrayPair:
        arrs = empty_array_pair()
        for b in self.buckets:
            arrs.apply_union(b.get_all())
        return arrs

    def bucket_report(self):
        ls = []
        for i, min_hash in enumerate(self.bucket_min_hashes):
            bucket = self.buckets[i]
            ls.append((min_hash, "size:", len(bucket), type(self.buckets[i]).__name__))
        return ls
