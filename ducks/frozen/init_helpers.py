import numpy as np
from typing import Union, Callable
from ducks.utils import get_attribute, make_empty_array


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
