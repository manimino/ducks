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


def sort_by_hash(
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
    obj_arr = np.empty(len(objs), dtype='O')
    for i, obj in enumerate(objs):
        val_arr[i] = get_field(obj, field)
        hash_arr[i] = hash(val_arr[i])
        obj_arr[i] = obj
    sort_order = np.argsort(hash_arr)
    val_arr = val_arr[sort_order]
    obj_arr = obj_arr[sort_order]
    return hash_arr, val_arr, obj_arr


def group_by_val(hash_arr: np.ndarray, val_arr: np.ndarray, obj_arr: np.ndarray):
    """Modifies val_arr and obj_arr so that they group elements having the same value.

    Does not modify hash_arr, as we won't need it past this point.

    """
    def _group_by_val_same_hash(val_arr, obj_arr, p0, p1):
        """Does group_by for a subarray all having the same hash but containing >=2 distinct values.

        Normal tools for doing group_by fail here.
        - We can't assume values are sortable, so can't just sort the values and find change points.
        - We are grouping values that have the same hash, so dict() will be inefficient.

        So just making a list for each distinct value and appending the indices to it will work.
        That will be O(n*k), where k = num of distinct values.
        Luckily, we don't expect too many distinct values with the same hash.
        Having more than two hashes colliding probably means the user is doing something funky, and bad
        performance is ok in that case.
        """
        distinct_vals = []
        val_idx_lists = []  # list of list of indices. All elements in the inner list have the same val.
        for i in range(p0, p1):
            try:
                idx = distinct_vals.index(val_arr[i])
                val_idx_lists[idx].append(i)
            except ValueError:
                distinct_vals.append(val_arr[i])
                val_idx_lists.append([i])

        # concat the val_idx_lists to make one array of indices, like how argsort output looks
        sort_idxs = []
        for ixl in val_idx_lists:
            sort_idxs.extend(ixl)

        # now apply that to each array inplace
        val_arr[p0:p1] = val_arr[sort_idxs]
        obj_arr[p0:p1] = obj_arr[sort_idxs]

    mismatch_hash = hash_arr[1:] != hash_arr[:-1]
    hash_change_pts = np.append(np.where(mismatch_hash), len(hash_arr) - 1)
    p0 = 0
    for end_i in hash_change_pts:
        p1 = end_i + 1
        if p1-p0 > 1:
            v = val_arr[p0]
            non_v_values = np.where(val_arr[p0+1:p1] != v)
            if len(non_v_values):  # False unless there's a hash collision
                _group_by_val_same_hash(val_arr, obj_arr, p0, p1)
        p0 = p1


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


def compute_mutable_dict(objs, field):
    """Create a dict of {val: obj_ids}. Used when creating a mutable index."""
    sorted_hashes, sorted_vals, sorted_objs = sort_by_hash(objs, field)
    group_by_val(sorted_hashes, sorted_vals, sorted_objs)
    starts, counts, unique_vals = run_length_encode(sorted_vals)
    d = dict()
    for i, v in enumerate(unique_vals):
        start = starts[i]
        count = counts[i]
        if counts[i] > SIZE_THRESH:
            d[v] = Int64Set(id(obj) for obj in sorted_objs[start:start+count])
        else:
            d[v] = tuple(id(obj) for obj in sorted_objs[start:start+count])
    return d
