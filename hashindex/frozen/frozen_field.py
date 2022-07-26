import numpy as np

from hashindex.frozen.array_pair import ArrayPair, make_array_pair, make_empty_array_pair
from typing import Union, Callable, Iterable, Any
from hashindex.init_helpers import sort_by_hash, group_by_val, run_length_encode
from hashindex.constants import SIZE_THRESH
from bisect import bisect_left, bisect_right
from dataclasses import dataclass


@dataclass
class ObjsByHash:
    sorted_hashes: np.ndarray
    sorted_objs: np.ndarray
    sorted_vals: np.ndarray
    unique_hashes: np.ndarray
    hash_starts: np.ndarray
    hash_run_lengths: np.ndarray

    def get(self, val):
        val_hash = hash(val)
        i = bisect_left(self.unique_hashes, val_hash)
        if i < 0 or i >= len(self.unique_hashes) or self.unique_hashes[i] != val_hash:
            raise KeyError('not in here')
        start = self.hash_starts[i]
        end = self.hash_starts[i] + self.hash_run_lengths[i]
        # Typically the hash will only contain the one val we want.
        # But hash collisions do happen.
        # Shrink the range until it contains only our value.
        while self.sorted_vals[start] != val:
            start += 1
        while self.sorted_vals[end-1] != val:
            end -= 1
        return make_array_pair(self.sorted_objs[start:end])


class FrozenFieldIndex:
    """Stores data and handles requests that are relevant to a single attribute of a FrozenHashIndex."""

    def __init__(self, field: Union[str, Callable], objs: Iterable[Any]):
        # sort the objects by attribute value, using their hashes and handling collisions
        sorted_hashes, sorted_vals, sorted_objs = sort_by_hash(objs, field)
        group_by_val(sorted_hashes, sorted_vals, sorted_objs)

        # find runs of the same value, get the start positions and lengths of those runs
        val_starts, val_run_lengths, unique_vals = run_length_encode(sorted_vals)

        # Pre-bake a dict of {val: array_pair} where there are many objs with the same val.
        self.val_to_arr_pair = dict()
        unused = np.ones_like(sorted_objs, dtype='bool')
        unused_count = len(unused)
        for i, val in enumerate(unique_vals):
            if val_run_lengths[i] > SIZE_THRESH:
                # extract these
                start = val_starts[i]
                end = start + val_run_lengths[i]
                unused[start:end] = False
                unused_count -= val_run_lengths[i]
                obj_arr = sorted_objs[start:end]
                self.val_to_arr_pair[val] = make_array_pair(obj_arr)

        # Put all remaining objs into one big object array 'objs_by_hash'.
        # During query, use bisection on the hash value to locate objects.
        # ArrayPairs will be made during query.
        if unused_count == 0:
            self.objs_by_hash = None
            return

        hash_starts, hash_run_lengths, unique_hashes = run_length_encode(sorted_hashes)
        if unused_count == len(sorted_objs):
            self.objs_by_hash = ObjsByHash(
                sorted_objs=sorted_objs,
                sorted_vals=sorted_vals,
                sorted_hashes=sorted_hashes,
                unique_hashes=unique_hashes,
                hash_starts=hash_starts,
                hash_run_lengths=hash_run_lengths
            )
            return

        unused_idx = np.where(unused)
        sorted_objs = sorted_objs[unused_idx]
        sorted_hashes = sorted_hashes[unused_idx]
        sorted_vals = sorted_vals[unused_idx]
        self.objs_by_hash = ObjsByHash(
            sorted_objs=sorted_objs,
            sorted_vals=sorted_vals,
            sorted_hashes=sorted_hashes,
            unique_hashes=unique_hashes,
            hash_starts=hash_starts,
            hash_run_lengths=hash_run_lengths
        )

    def get(self, val) -> ArrayPair:
        if val in self.val_to_arr_pair:
            print(val, self.val_to_arr_pair[val])
            return self.val_to_arr_pair[val]
        elif self.objs_by_hash is not None:
            return self.objs_by_hash.get(val)

    def get_obj_ids(self, val) -> np.ndarray:
        return self.get(val).id_arr

    def get_all(self) -> ArrayPair:
        arrs = make_empty_array_pair()
        for v in self.big_vals:
            arrs.apply_union(self.big_vals[v])
        small = make_array_pair(self.sm_objs)
        arrs.apply_union(small)
        return arrs

    def __iter__(self):
        return FrozenFieldIndexIterator(self)

    def __len__(self):
        return len(self.sm_objs) + sum([len(v) for v in self.big_vals.values()])


class FrozenFieldIndexIterator:
    def __init__(self, ffi: FrozenFieldIndex):
        self.sm_objs = ffi.sm_objs
        self.i = 0
        self.big_iter = iter(ffi.big_vals.values())
        self.cur_arr = None
        self.did_small = False

    def __next__(self):
        while True:
            # smalls first
            if not self.did_small:
                if self.i == len(self.sm_objs):
                    self.did_small = True
                    self.i = 0
                else:
                    obj = self.sm_objs[self.i]
                    self.i += 1
                    return obj

            # now each large
            if self.cur_arr is None:
                self.cur_arr = next(self.big_iter).obj_arr
                self.i = 0
                continue
            if self.i == len(self.cur_arr):
                self.cur_arr = None
                continue
            obj = self.cur_arr[self.i]
            self.i += 1
            return obj
