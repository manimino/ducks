import numpy as np
import sortednp as snp
from dataclasses import dataclass
from hashindex.init_helpers import BucketPlan
from hashindex.utils import get_field
from typing import Callable, Union


@dataclass
class ArrayPair:
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


def make_array_pair(obj_arr: np.ndarray):
    """Finds obj_ids and sorts obj_arr by the ids. Returns an ArrayPair."""
    obj_ids = np.empty_like(obj_arr, dtype="int64")
    for i, obj in enumerate(obj_arr):
        obj_ids[i] = id(obj)
    sort_order = np.argsort(obj_ids)
    return ArrayPair(id_arr=obj_ids[sort_order], obj_arr=obj_arr[sort_order])


def empty_array_pair() -> ArrayPair:
    return ArrayPair(
        id_arr=np.array([], dtype="int64"), obj_arr=np.array([], dtype="O")
    )


class FHashBucket:
    def __init__(self, bp: BucketPlan, field: Union[str, Callable]):
        self.array_pair = make_array_pair(bp.obj_arr)
        self.field = field

    def get(self, val):
        match_pos = []
        for i in range(len(self)):
            obj_val = get_field(self.array_pair.obj_arr[i], self.field)
            if obj_val == val or obj_val is val:
                match_pos.append(i)
        return ArrayPair(
            id_arr=self.array_pair.id_arr[match_pos],
            obj_arr=self.array_pair.obj_arr[match_pos],
        )

    def get_all(self):
        return self.array_pair

    def __len__(self):
        return len(self.array_pair)


class FDictBucket:
    def __init__(self, bp: BucketPlan, field: Union[str, Callable]):
        self.field = field
        first = bp.val_arr[
            0
        ]  # assumption: bp will never be empty (true as long as bucket size limit >= 1)
        if all(val == first for val in bp.val_arr):
            # In the overwhelming majority of cases, val will be unique.
            self.d = {first: make_array_pair(bp.obj_arr)}
        else:
            # Building a dict requires hashing every value, so there's some time cost here (~1s per 1M items).
            # Maybe worse since, as we know, the value hashes collide.
            d_idx = dict()
            for i, val in enumerate(bp.val_arr):
                if val not in self.d:
                    d_idx[val] = []
                d_idx[val].append(i)
            for val in self.d_idx:
                self.d[val] = bp.obj_arr[d_idx[val]]

    def get_all(self):
        arrs = empty_array_pair()
        for val in self.d:
            arrs.apply_union(self.d[val])
        return arrs

    def get(self, val):
        return self.d.get(val, empty_array_pair())

    def __len__(self):
        return sum(len(self.d[val]) for val in self.d)
