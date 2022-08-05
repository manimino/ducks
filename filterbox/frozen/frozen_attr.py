"""
Performs object lookup for a single attribute in a FrozenFilterBox.
"""


import numpy as np

from bisect import bisect_left
from dataclasses import dataclass
from typing import Union, Callable, Set

from filterbox.init_helpers import sort_by_hash, group_by_val, run_length_encode
from filterbox.constants import SIZE_THRESH
from filterbox.utils import make_empty_array


@dataclass
class ObjsByHash:
    sorted_obj_ids: np.ndarray
    sorted_vals: np.ndarray
    unique_hashes: np.ndarray
    hash_starts: np.ndarray
    hash_run_lengths: np.ndarray
    dtype: str

    def get(self, val):
        val_hash = hash(val)
        i = bisect_left(self.unique_hashes, val_hash)
        if i < 0 or i >= len(self.unique_hashes) or self.unique_hashes[i] != val_hash:
            return make_empty_array(self.dtype)
        start = self.hash_starts[i]
        end = self.hash_starts[i] + self.hash_run_lengths[i]
        # Typically the hash will only contain the one val we want.
        # But hash collisions do happen.
        # Shrink the range until it contains only our value.
        while start < end and self.sorted_vals[start] != val:
            start += 1
        while end > start and self.sorted_vals[end - 1] != val:
            end -= 1
        if end == start:
            return make_empty_array(self.dtype)
        return self.sorted_obj_ids[start:end]


class FrozenAttrIndex:
    """Stores data and handles requests that are relevant to a single attribute of a FrozenFilterBox."""

    def __init__(self, attr: Union[str, Callable], objs: np.ndarray, dtype: str):
        # sort the objects by attribute value, using their hashes and handling collisions
        self.dtype = dtype
        obj_id_arr = np.arange(len(objs), dtype=self.dtype)
        sorted_hashes, sorted_vals, sorted_obj_ids = sort_by_hash(
            objs, obj_id_arr, attr
        )
        group_by_val(sorted_hashes, sorted_vals, sorted_obj_ids)

        # find runs of the same value, get the start positions and lengths of those runs
        val_starts, val_run_lengths, unique_vals = run_length_encode(sorted_vals)

        # Pre-bake a dict of {val: array_pair} where there are many objs with the same val.
        self.val_to_obj_ids = dict()
        unused = np.ones_like(sorted_obj_ids, dtype="bool")
        n_unused = len(unused)
        for i, val in enumerate(unique_vals):
            if val_run_lengths[i] > SIZE_THRESH:
                # extract these
                start = val_starts[i]
                end = start + val_run_lengths[i]
                unused[start:end] = False
                n_unused -= val_run_lengths[i]
                obj_id_arr = sorted_obj_ids[start:end]
                self.val_to_obj_ids[val] = np.sort(obj_id_arr)

        # Put all remaining objs into one big object array 'objs_by_hash'.
        # During query, use bisection on the hash value to locate objects.
        # The output obj_id_arrays will be made during query.
        if n_unused == 0:
            self.objs_by_hash = None
            return

        if n_unused == len(sorted_obj_ids):
            hash_starts, hash_run_lengths, unique_hashes = run_length_encode(
                sorted_hashes
            )
            self.objs_by_hash = ObjsByHash(
                sorted_obj_ids=sorted_obj_ids,
                sorted_vals=sorted_vals,
                unique_hashes=unique_hashes,
                hash_starts=hash_starts,
                hash_run_lengths=hash_run_lengths,
                dtype=self.dtype,
            )
            return

        # we have a mix of cardinalities
        unused_idx = np.where(unused)
        sorted_obj_ids = sorted_obj_ids[unused_idx]
        sorted_hashes = sorted_hashes[unused_idx]
        sorted_vals = sorted_vals[unused_idx]
        hash_starts, hash_run_lengths, unique_hashes = run_length_encode(sorted_hashes)
        self.objs_by_hash = ObjsByHash(
            sorted_obj_ids=sorted_obj_ids,
            sorted_vals=sorted_vals,
            unique_hashes=unique_hashes,
            hash_starts=hash_starts,
            hash_run_lengths=hash_run_lengths,
            dtype=self.dtype,
        )

    def get(self, val) -> np.ndarray:
        """Get indices of objects whose attribute is val."""
        if val in self.val_to_obj_ids:
            # these are stored in sorted order
            return self.val_to_obj_ids[val]
        elif self.objs_by_hash is not None:
            return np.sort(self.objs_by_hash.get(val))
        else:
            return make_empty_array(self.dtype)

    def get_all(self):
        """Get indices of every object with this attribute. Used when matching ANY."""
        if self.objs_by_hash is None:
            arrs = []
        else:
            arrs = [self.objs_by_hash.sorted_obj_ids]
        for v in self.val_to_obj_ids.values():
            arrs.append(v)
        return np.sort(np.concatenate(arrs))

    def get_values(self) -> Set:
        """Get each value we have objects for."""
        vals = set(self.val_to_obj_ids.keys())
        if self.objs_by_hash is not None:
            vals = vals.union(self.objs_by_hash.sorted_vals)
        return vals

    def __len__(self):
        tot = sum(len(v) for v in self.val_to_obj_ids.values())
        return tot + len(self.objs_by_hash.sorted_obj_ids)
