from dataclasses import dataclass

import numpy as np
import sortednp as snp
from typing import Optional


@dataclass
class ArrayPair:
    """Pair of sorted numpy arrays that act like a Python set of objects. Objects need not be hashable."""
    id_arr: np.ndarray
    obj_arr: np.ndarray

    def apply_intersection(self, other):
        """Compute the intersection of self and other. Preserves sort order. Update this object to the result."""
        intersect_ids, indices = snp.intersect(self.id_arr, other.id_arr, indices=True)
        self.obj_arr = self.obj_arr[indices[0]]
        self.id_arr = intersect_ids

    def apply_union(self, other):
        """Compute the sorted of self and other. Preserves sort order. Update this object to the result."""
        merged_id_arr, indices = snp.merge(
            self.id_arr, other.id_arr, indices=True, duplicates=snp.DROP
        )
        obj_arr = np.empty_like(merged_id_arr, dtype="O")
        obj_arr[indices[0]] = self.obj_arr
        obj_arr[indices[1]] = other.obj_arr
        self.id_arr = merged_id_arr
        self.obj_arr = obj_arr

    def apply_difference(self, other):
        """Compute the difference of self and other. Preserves sort order. Update this object to the result."""
        matched_positions = snp.intersect(self.id_arr, other.id_arr, indices=True)[1][0]
        matches = np.zeros_like(self.id_arr, dtype=bool)
        matches[matched_positions] = True
        self.id_arr = self.id_arr[~matches]
        self.obj_arr = self.obj_arr[~matches]

    def __len__(self):
        return len(self.id_arr)


def make_array_pair(obj_arr: np.ndarray, obj_ids: Optional[np.ndaray], sort_order: Optional[np.ndaray]):
    """Creates an ArrayPair. Finds obj_ids and sort_order if not provided."""
    if not obj_ids:
        obj_ids = np.empty_like(obj_arr, dtype="int64")
        for i, obj in enumerate(obj_arr):
            obj_ids[i] = id(obj)
    if not sort_order:
        sort_order = np.argsort(obj_ids)
    return ArrayPair(id_arr=obj_ids[sort_order], obj_arr=obj_arr[sort_order]), sort_order


def make_empty_array_pair() -> ArrayPair:
    """Creates an empty ArrayPair."""
    return ArrayPair(
        id_arr=np.array([], dtype="int64"), obj_arr=np.array([], dtype="O")
    )
