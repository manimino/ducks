"""
Performs object lookup for a single attribute in a FrozenFilterBox.
"""


import numpy as np

from bisect import bisect_left, bisect_right
from typing import Union, Callable, Set

from BTrees import OOBTree
from filterbox.constants import SIZE_THRESH
from filterbox.utils import make_empty_array
from filterbox.init_helpers import get_vals, run_length_encode


class FrozenAttrValIndex:
    """Stores data and handles requests that are relevant to a single attribute of a FrozenFilterBox."""

    def __init__(self, attr: Union[str, Callable], objs: np.ndarray, dtype: str):
        # sort the objects by attribute value, using their hashes and handling collisions
        self.dtype = dtype
        self.attr = attr
        obj_id_arr = np.arange(len(objs), dtype=self.dtype)
        for i, obj in enumerate(objs):
            obj_id_arr[i] = i
        obj_id_arr, val_arr = get_vals(objs, obj_id_arr, self.attr)
        sort_order = np.argsort(val_arr)  # throws TypeError if unsortable
        val_arr = val_arr[sort_order]
        obj_id_arr = obj_id_arr[sort_order]

        # Pull repeated attributes out into a BTree and pre-sort their indices.
        # Saves memory, and makes object lookups *way* faster.
        self.val_to_obj_ids = OOBTree()
        val_starts, val_run_lengths, unique_vals = run_length_encode(val_arr)
        unused = np.ones_like(obj_id_arr, dtype="bool")
        n_unused = len(unused)
        for i, val in enumerate(unique_vals):
            if val_run_lengths[i] > SIZE_THRESH:
                # extract these
                start = val_starts[i]
                end = start + val_run_lengths[i]
                unused[start:end] = False
                n_unused -= val_run_lengths[i]
                self.val_to_obj_ids[val] = np.sort(obj_id_arr[start:end])
        self.val_arr = val_arr[unused]
        self.obj_id_arr = obj_id_arr[unused]

    def get(self, val) -> np.ndarray:
        """Get indices of objects whose attribute is val."""
        if val in self.val_to_obj_ids:
            return self.val_to_obj_ids[val]
        left = bisect_left(self.val_arr, val)
        if left == len(self.val_arr) or self.val_arr[left] != val:
            return make_empty_array(self.dtype)
        right = bisect_right(self.val_arr, val)
        return np.sort(
            self.obj_id_arr[left:right]
        )  # TODO: consider storing large arrays in sorted order. Yeah, not optional, it's a huge perf difference.

    def get_all(self) -> np.ndarray:
        """Get indices of every object with this attribute. Used when matching ANY."""
        return np.sort(self.obj_id_arr)

    def get_values(self) -> Set:
        """Get each value we have objects for."""
        return set(self.val_arr)

    def get_ids_by_range(
        self, lo, hi, include_lo=False, include_hi=False
    ) -> np.ndarray:
        """Get the object IDs associated with this value range as an Int64Set. Only usable when self.d is a tree."""
        # Get matches from the val_to_obj_ids BTree

        # val_to_obj_ids.values(lo, hi)

        # Get the matches from the main array
        if len(self) == 0:
            return make_empty_array(self.dtype)
        if lo is None:
            left = 0
            lo = self.val_arr[0]
            include_lo = True
        else:
            left = bisect_left(self.val_arr, lo)
            while left < len(self.val_arr) and self.val_arr[left] < lo:
                left += 1

        if hi is None:
            right = len(self.val_arr)
            hi = self.val_arr[right - 1]
            include_hi = True
        else:
            right = bisect_right(self.val_arr, hi)
            while right > left and self.val_arr[right - 1] > hi:
                right -= 1

        # move left pointer up to fit > constraint
        if not include_lo:
            while left < len(self.val_arr) and self.val_arr[left] == lo:
                left += 1

        # move right pointer down to fit < constraint
        if not include_hi:
            while right > left and self.val_arr[right - 1] == hi:
                right -= 1

        # sort matching ids and return
        return np.sort(self.obj_id_arr[left:right])

    @staticmethod
    def get_index_type():
        return "tree"

    def __len__(self):
        return len(self.val_arr)
