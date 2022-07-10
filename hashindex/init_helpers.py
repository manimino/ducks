"""
When a large object list is provided in the constructor -- i.e., HashIndex(objs, on={...}) has lots of objs,
adding the objs one at a time is naive and slow. Buckets will be created, overfilled, and split needlessly.
There is a ~10X performance benefit to examining the objs and constructing all the needed buckets just once.

The functions here provide that speedup. They have been squeezed pretty hard for performance. It matters here!
Building the index is most likely going to be the bottleneck when working with large datasets, especially in the
expected applications for this library.

Workflow:
 - Hash the given attribute for all objs
 - Sort the hashes
 - Get counts of each unique hash (via run-length encoding)
 - Use a cumulative sum-like algorithm to determine the span of each bucket
 - Return all information that init needs to create buckets

Running the workflow takes between 600ms (low-cardinality case) and 800ms (high-cardinality case) on a 1M-item dataset.
"""

import numpy as np
from numba import njit
from dataclasses import dataclass
from typing import Tuple, List, Union, Callable, Any
from hashindex.utils import get_field
from operator import itemgetter


def get_sorted_hashes(objs: List[Any], field: Union[Callable, str]) -> Tuple[np.array, np.ndarray]:
    """
    Hash the given attribute for all objs. Sort objs and hashes by the hashes.

    Takes 450ms for 1M objs on a numeric field. May take longer if field is a Callable or is hard to hash.
    Breakdown:
     - 100ms to do all the get_field() calls. Cost is the part that inspects each obj to see if it's a dict.
     - 220ms to get and hash the field for each obj. No getting around that.
     - 100ms to sort the hashes
     - 30ms of whatever
    """
    hashes = np.fromiter((hash(get_field(obj, field)) for obj in objs), dtype='int64')
    pos = np.argsort(hashes)
    sorted_hashes = hashes[pos]
    sorted_objs = itemgetter(*pos)(objs)  # todo handle itemgetter len 0, 1 weirdness
    return sorted_hashes, sorted_objs


def run_length_encode(sorted_hashes: np.ndarray):
    """
    Find counts of each hash in sorted_hashes via run-length encoding.

    Takes 10ms for 1M objs.
    """
    mismatch = sorted_hashes[1:] != sorted_hashes[:-1]
    i = np.append(np.where(mismatch), len(sorted_hashes) - 1)
    counts = np.diff(np.append(-1, i))
    starts = np.cumsum(np.append(0, counts))[:-1]
    return starts, counts, sorted_hashes[i]


@njit
def find_bucket_starts(counts, limit):
    """
    Find the start positions for each bucket via a cumulative sum that resets when limit is exceeded.

    Takes about 1ms for a counts length of 1M. Without @njit, it would take 300ms instead - great speedup here.
    """
    result = np.empty(len(counts), dtype=np.uint64)
    total = 0
    idx = 0
    for i, count in enumerate(counts):
        total += count
        if total > limit:
            total = count
            result[idx] = i
            idx += 1
    return result[:idx]


@dataclass
class BucketPlan:
    distinct_hashes: np.ndarray
    distinct_hash_counts: np.ndarray
    obj_arr: np.ndarray
    hash_arr: np.ndarray

    def __str__(self):
        d = dict(zip(self.distinct_hashes, self.distinct_hash_counts))
        l1 = len(self.obj_arr)
        l2 = len(self.hash_arr)
        mh = min(self.hash_arr)
        return f'{mh}: {l1}={l2}; ' + str(d)


def compute_buckets(objs, field, bucket_size_limit):
    sorted_hashes, sorted_objs = get_sorted_hashes(objs, field)
    starts, counts, val_hashes = run_length_encode(sorted_hashes)
    bucket_starts = find_bucket_starts(counts, bucket_size_limit)

    bucket_plans = []
    for i, s in enumerate(bucket_starts):
        if i + 1 == len(bucket_starts):
            distinct_hashes = val_hashes[s:]
            distinct_hash_counts = counts[s:]
            obj_arr = sorted_objs[starts[s]:]
            hash_arr = sorted_hashes[starts[s]:]
        else:
            t = bucket_starts[i + 1]
            distinct_hashes = val_hashes[s:t]
            distinct_hash_counts = counts[s:t]
            obj_arr = sorted_objs[starts[s]:starts[t]]
            hash_arr = sorted_hashes[starts[s]:starts[t]]
        bucket_plans.append(
            BucketPlan(
                distinct_hashes=distinct_hashes,
                distinct_hash_counts=distinct_hash_counts,
                obj_arr=obj_arr,
                hash_arr=hash_arr,
            )
        )
    return bucket_plans
