"""
When HashIndex is initialized with objects, it would be slow to add the objects one at a time. Instead, we can
analyze the list of objects, plan out which buckets will be created, and put the objects in those buckets.

There is a ~10X performance benefit to examining the objs and constructing all the needed buckets just once.

The functions here provide that speedup. They have been squeezed pretty hard for performance. It matters here!
Building the index is most likely going to be the bottleneck when working with large datasets, especially in the
expected applications for this library.

Workflow:
 - Hash the given attribute for all objs
 - Sort the hashes
 - Get counts of each unique hash (via run-length encoding)
 - Use a cumulative sum-like algorithm to determine the span of each bucket
 - Return all information that init needs to create buckets containing the objects (a list of `BucketPlan`)

Running the workflow takes between 600ms (low-cardinality case) and 800ms (high-cardinality case) on a 1M-item dataset.
"""

import numpy as np
from typing import Tuple, Union, Callable, Any, Iterable
from hashindex.utils import get_field
from hashindex.constants import SIZE_THRESH
from cykhash import Int64Set


def hash_and_sort(
    objs: Iterable[Any], field: Union[Callable, str]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Sort objs and vals by vals.

    Takes 450ms for 1M objs on a numeric field. May take longer if field is a Callable or is hard to hash.
    Breakdown:
     - 100ms to do all the get_field() calls. Cost is the part that inspects each obj to see if it's a dict.
     - 220ms to get and hash the field for each obj. No getting around that.
     - 100ms to sort the hashes
     - 30ms of whatever
    """
    hash_arr = np.empty(len(objs), dtype='int64')
    val_arr = np.empty(len(objs), dtype='O')
    obj_arr = np.array(objs, dtype='O')
    for i, o in enumerate(objs):
        val_arr[i] = get_field(o, field)
        objs[i] = get_field(o, field)
    sort_order = np.argsort(hash_arr)
    val_arr = val_arr[sort_order]
    obj_arr = obj_arr[sort_order]
    return hash_arr, val_arr, obj_arr


def group_equal_vals(hash_arr: np.ndarray, val_arr: np.ndarray, obj_arr: np.ndarray):
    """
    Normal tools for doing group_by fail here.
    - We can't assume sortability, so can't sort 'em and find change points.
    - We are grouping values that have the same hash, so we can't put them in a dict() either.
    Luckily, we don't expect too many distinct values with the same hash. So just making a list for each
    distinct value and appending the indices to it will be O(n*k) where k = num of distinct values. Not too too bad.
    """
    mismatch_hash = hash_arr[1:] != hash_arr[:-1]
    change_pts = np.append(np.where(mismatch_hash), len(val_arr) - 1)



def run_length_encode(val_arr: np.ndarray):
    """
    Find counts of each val in the val_arr (sorted) via run-length encoding.

    Takes 10ms for 1M objs.
    """
    mismatch_val = val_arr[1:] != val_arr[:-1]
    change_pts = np.append(np.where(mismatch_val), len(val_arr) - 1)
    counts = np.diff(np.append(-1, change_pts))
    starts = np.cumsum(np.append(0, counts))[:-1]
    return starts, counts, val_arr[change_pts]


def compute_dict(objs, field):
    """Create a dict of {val: obj_ids}. Used when creating a mutable index."""
    sorted_hashes, sorted_vals, sorted_objs = hash_and_sort(objs, field)
    starts, counts, unique_hashes = run_length_encode(sorted_hashes)
    d = dict()
    for i, v in enumerate(unique_vals):
        start = starts[i]
        count = counts[i]
        if counts[i] > SIZE_THRESH:
            d[v] = Int64Set(id(obj) for obj in sorted_objs[start:start+count])
        else:
            d[v] = tuple(id(obj) for obj in sorted_objs[start:start+count])
    return d


def compute_frozen_data(objs, field):
    sorted_hashes, sorted_vals, sorted_objs = hash_and_sort(objs, field)
    sorted_obj_ids = np.empty_like(sorted_objs, dtype='int64')
    for i, obj in enumerate(sorted_objs):
        sorted_obj_ids[i] = id(obj)
    starts, counts, unique_vals = run_length_encode(sorted_vals)
