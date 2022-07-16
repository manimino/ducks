import bisect

from hashindex.init_helpers import BucketPlan
from hashindex.constants import SIZE_THRESH
from hashindex.frozen_buckets import FDictBucket, FHashBucket, ArrayPair
from typing import List, Union, Callable


class FrozenFieldIndex:

    def __init__(self, bucket_plans: List[BucketPlan], field: Union[str, Callable]):
        self.buckets = []
        self.bucket_min_hashes = []
        for bp in bucket_plans:
            if len(bp.distinct_hash_counts) == 1 and bp.distinct_hash_counts > SIZE_THRESH:
                b = FDictBucket(bp, self.field)
            else:
                b = FHashBucket(bp, self.field)
            lowest_hash = min(bp.distinct_hashes)
            self.bucket_min_hashes.append(lowest_hash)
            self.buckets.append(b)

    def get(self, val):
        val_hash = hash(val)
