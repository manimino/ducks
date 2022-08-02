"""
When HashBox is initialized with objects, it would be slow to add the objects one at a time. Instead, we can
analyze the list of objects, plan out which containers will be created, and put the objects in those containers.

These functions are also used during FrozenHashBox creation, although the final data structures there are different.

Workflow:
 - Hash the given attribute for all objs
 - Sort the hashes
 - Group within each hash by matching value
 - Get counts of each unique hash (via run-length encoding)
 - Return all information that init needs to create containers for the objects

Note that we cannot simply sort by value; the values may not be comparable. Hence we hash, then group by value.

The total time is very close to simply making a dict-of-set for all objects; it's about the best you can do in Python.
Running the workflow takes between 600ms (low-cardinality case) and 1.5s (high-cardinality case) on a 1M-item dataset.
"""

import numpy as np
from typing import Tuple, Union, Callable, Any, Iterable
from hashbox.utils import get_attribute, make_empty_array
from hashbox.constants import SIZE_THRESH
from cykhash import Int64Set


def sort_by_hash(
    objs: np.ndarray, obj_id_arr: np.ndarray, attr: Union[Callable, str]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fetch vals from each obj. Create obj_id, val, and hash arrays, sorted by hash."""
    hash_arr = np.empty(len(objs), dtype="int64")
    val_arr = np.empty(len(objs), dtype="O")
    success = np.empty(len(objs), dtype=bool)
    for i, obj in enumerate(objs):
        val_arr[i], success[i] = get_attribute(obj, attr)
        hash_arr[i] = hash(val_arr[i])

    hash_arr = hash_arr[success]
    val_arr = val_arr[success]
    obj_id_arr = obj_id_arr[success]

    sort_order = np.argsort(hash_arr)
    val_arr = val_arr[sort_order]
    obj_id_arr = obj_id_arr[sort_order]
    hash_arr = hash_arr[sort_order]
    return hash_arr, val_arr, obj_id_arr


def group_by_val(hash_arr: np.ndarray, val_arr: np.ndarray, obj_id_arr: np.ndarray):
    """Modifies val_arr, hash_arr, and obj_id_arr so that they group elements having the same value."""

    def _group_by_val_same_hash(val_arr, obj_id_arr, p0, p1):
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
        val_idx_lists = (
            []
        )  # list of list of indices. All elements in the inner list have the same val.
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
        obj_id_arr[p0:p1] = obj_id_arr[sort_idxs]
        hash_arr[p0:p1] = hash_arr[sort_idxs]

    mismatch_hash = hash_arr[1:] != hash_arr[:-1]
    hash_change_pts = np.append(np.where(mismatch_hash), len(hash_arr) - 1)
    p0 = 0
    for end_i in hash_change_pts:
        p1 = end_i + 1
        if p1 - p0 > 1:
            v = val_arr[p0]
            non_v_values = np.where(val_arr[p0 + 1 : p1] != v)
            if len(non_v_values):  # False unless there's a hash collision
                _group_by_val_same_hash(val_arr, obj_id_arr, p0, p1)
        p0 = p1


def run_length_encode(arr: np.ndarray):
    """
    Find counts of each element in the arr (sorted) via run-length encoding.

    Takes 10ms for 1M objs.
    """
    if len(arr) == 0:
        return (
            make_empty_array("int64"),
            make_empty_array("int64"),
            make_empty_array("int64"),
        )
    mismatch_val = arr[1:] != arr[:-1]
    change_pts = np.append(np.where(mismatch_val), len(arr) - 1)
    counts = np.diff(np.append(-1, change_pts))
    starts = np.cumsum(np.append(0, counts))[:-1]
    return starts, counts, arr[change_pts]


def compute_mutable_dict(objs: Iterable[Any], attr: Union[str, Callable]):
    """Create a dict of {val: obj_ids}. Used when creating a mutable index."""
    obj_arr = np.empty(len(objs), dtype="O")
    obj_id_arr = np.empty(len(objs), dtype="int64")
    for i, obj in enumerate(objs):
        obj_arr[i] = obj
        obj_id_arr[i] = id(obj)

    sorted_hashes, sorted_vals, sorted_obj_ids = sort_by_hash(obj_arr, obj_id_arr, attr)
    group_by_val(sorted_hashes, sorted_vals, sorted_obj_ids)
    starts, counts, unique_vals = run_length_encode(sorted_vals)
    d = dict()
    for i, v in enumerate(unique_vals):
        start = starts[i]
        count = counts[i]
        if counts[i] > SIZE_THRESH:
            d[v] = Int64Set(sorted_obj_ids[start : start + count])
        elif counts[i] == 1:
            d[v] = sorted_obj_ids[start]
        else:
            d[v] = tuple(sorted_obj_ids[start : start + count])
    return d
