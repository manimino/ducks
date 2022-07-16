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
from hashindex.constants import HASH_MIN
from dataclasses import dataclass
from typing import Tuple, List, Union, Callable, Any, Iterable
from hashindex.utils import get_field


def get_sorted_hashes(objs: List[Any], field: Union[Callable, str]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Hash the given attribute for all objs. Sort objs and hashes by the hashes.

    Takes 450ms for 1M objs on a numeric field. May take longer if field is a Callable or is hard to hash.
    Breakdown:
     - 100ms to do all the get_field() calls. Cost is the part that inspects each obj to see if it's a dict.
     - 220ms to get and hash the field for each obj. No getting around that.
     - 100ms to sort the hashes
     - 30ms of whatever
    """
    vals = np.empty((len(objs,)), dtype='O')
    for i, obj in enumerate(objs):
        vals[i] = get_field(obj, field)
    hashes = np.fromiter((hash(val) for val in vals), dtype='int64')
    pos = np.argsort(hashes)
    sorted_hashes = hashes[pos]
    sorted_objs = np.empty_like(hashes, dtype='O')
    for i in pos:
        sorted_objs[pos[i]] = objs[i]
    sorted_vals = vals[pos]
    return sorted_vals, sorted_hashes, sorted_objs


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


def find_bucket_starts(counts, limit):
    """
    Find the start positions for each bucket via a cumulative sum that resets when limit is exceeded.

    inputs:
        counts, a histogram of the number of values with each hash, e.g. [1 1000 1 1 1 1]
        limit, a maximum of how many items can fit in a multi-item bucket
    output:
        an array of start positions such that each bucket multi-item bucket contains <= limit values
        e.g. [0, 1, 2] for the example input

    Note: This function is ridiculously faster (like 300x) if decorated with @numba.njit.
    However, numba is a difficult dependency to add, as it conflicts with recent numpy. And numpy updates
    are constantly required due to security updates. So, we can't use numba here despite its amazing performance.
    """
    result = np.empty(len(counts), dtype=np.uint64)
    idx = 0
    total = 0
    for i, count in enumerate(counts):
        total += count
        if total > limit or idx == 0:
            # we're overfilled; start a new bucket at this position to hold the current count
            total = count
            result[idx] = i
            idx += 1
    return result[:idx]


@dataclass
class BucketPlan:
    distinct_hashes: np.ndarray
    distinct_hash_counts: np.ndarray
    obj_arr: np.ndarray
    hash_arr: Iterable[Any]
    val_arr: np.ndarray

    def __str__(self):
        d = dict(zip(self.distinct_hashes, self.distinct_hash_counts))
        l1 = len(self.obj_arr)
        l2 = len(self.hash_arr)
        l3 = len(self.val_arr)
        mh = min(self.hash_arr)
        return f'{mh}: {l1}={l2}={l3}; ' + str(d)


def compute_buckets(objs, field, bucket_size_limit):
    sorted_vals, sorted_hashes, sorted_objs = get_sorted_hashes(objs, field)
    starts, counts, val_hashes = run_length_encode(sorted_hashes)
    bucket_starts = find_bucket_starts(counts, bucket_size_limit)

    bucket_plans = []
    for i, s in enumerate(bucket_starts):
        if i + 1 == len(bucket_starts):
            distinct_hashes = val_hashes[s:]
            distinct_hash_counts = counts[s:]
            obj_arr = sorted_objs[starts[s]:]
            hash_arr = sorted_hashes[starts[s]:]
            val_arr = sorted_vals[starts[s]:]
        else:
            t = bucket_starts[i + 1]
            distinct_hashes = val_hashes[s:t]
            distinct_hash_counts = counts[s:t]
            obj_arr = sorted_objs[starts[s]:starts[t]]
            hash_arr = sorted_hashes[starts[s]:]
            val_arr = sorted_vals[starts[s]:starts[t]]
        bucket_plans.append(
            BucketPlan(
                distinct_hashes=distinct_hashes,
                distinct_hash_counts=distinct_hash_counts,
                obj_arr=obj_arr,
                hash_arr=hash_arr,
                val_arr=val_arr
            )
        )

    return bucket_plans
