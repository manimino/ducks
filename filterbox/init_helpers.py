"""
When FilterBox is initialized with objects, it would be slow to add the objects one at a time. Instead, we can
analyze the list of objects, plan out which containers will be created, and put the objects in those containers.

These functions are also used during FrozenFilterBox creation, although the final data structures there are different.

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
from array import array
from typing import Tuple, Union, Callable, Any, Iterable
from filterbox.utils import get_attribute, make_empty_array
from filterbox.constants import ARR_TYPE, ARRAY_SIZE_MAX
from cykhash import Int64Set


def get_vals(objs: np.ndarray, obj_id_arr: np.ndarray, attr: Union[Callable, str]):
    """Gets vals by attribute. Returned arrays will be shorter than input if objects are missing attributes."""
    val_arr = np.empty(len(objs), dtype="O")
    success = np.empty(len(objs), dtype=bool)
    for i, obj in enumerate(objs):
        val_arr[i], success[i] = get_attribute(obj, attr)

    val_arr = val_arr[success]
    obj_id_arr = obj_id_arr[success]
    return obj_id_arr, val_arr


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
