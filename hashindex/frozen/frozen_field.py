import numpy as np

from hashindex.frozen.array_pair import ArrayPair, make_array_pair, make_empty_array_pair
from typing import Union, Callable, Iterable, Any
from hashindex.init_helpers import sort_by_hash, group_by_val, run_length_encode
from hashindex.constants import SIZE_THRESH
from bisect import bisect_left, bisect_right

class FrozenFieldIndex:
    """Stores data and handles requests that are relevant to a single attribute of a FrozenHashIndex."""

    def __init__(self, field: Union[str, Callable], objs: Iterable[Any]):
        # sort the objects by attribute value, using their hashes and handling collisions
        sorted_hashes, sorted_vals, sorted_objs = sort_by_hash(objs, field)
        group_by_val(sorted_hashes, sorted_vals, sorted_objs)

        # find runs of the same value, get the start positions and lengths of those runs
        starts, run_lengths, unique_vals = run_length_encode(sorted_vals)

        # build obj_ids array
        self.obj_ids = np.empty_like(sorted_objs, dtype='int64')
        for i, obj in enumerate(sorted_objs):
            self.obj_ids[i] = id(obj)

        # pre-create ArrayPairs for values that have many object that are sorted by obj_id.
        unused = np.ones_like(sorted_objs, dtype='bool')
        self.big_vals = dict()
        remaining_count = len(sorted_objs)
        for i, v in enumerate(unique_vals):
            if run_lengths[i] > SIZE_THRESH:
                start = starts[i]
                end = start + run_lengths[i]
                obj_arr = sorted_objs[start:end]
                self.big_vals[v] = make_array_pair(obj_arr)
                unused[start:end] = False
                remaining_count -= run_lengths[i]

        # Vals with few objs go in small_vals, which is a single array sorted by val.
        # We'll create id-sorted ArrayPairs from it on demand.
        # or better idea, we'll binary search it on demand.
        if remaining_count == len(sorted_objs):
            self.sm_objs = sorted_objs
            self.sm_unique_vals = unique_vals
            self.sm_starts = starts
            self.sm_run_lengths = run_lengths
            return

        self.sm_objs = np.empty(remaining_count, dtype='O')
        n_sm_vals = len(unique_vals) - len(self.big_vals)
        self.sm_unique_vals = np.empty(n_sm_vals, dtype='O')
        self.sm_starts = np.empty(n_sm_vals, dtype='O')
        self.sm_run_lengths = np.empty(n_sm_vals, dtype='O')
        obj_pos = 0
        i_pos = 0
        for i, v in enumerate(unique_vals):
            if run_lengths[i] <= SIZE_THRESH:
                start = starts[i]
                end = start + run_lengths[i]
                self.sm_objs[obj_pos: obj_pos+run_lengths[i]] = sorted_objs[start:end]
                self.sm_unique_vals[i_pos] = v
                self.sm_starts[i_pos] = obj_pos
                self.sm_run_lengths[i_pos] = run_lengths[i]
                obj_pos += run_lengths[i]
                i_pos += 1

        """
        self.small_vals_to_pos = dict()
        size = len(np.where(unused)[0])
        self.small_objs = np.empty((size,), dtype='O')
        pos_len = len(unique_vals) - len(self.big_vals)
        self.small_starts = np.empty((pos_len,), dtype='int32')
        self.small_lengths = np.empty((pos_len,), dtype='int32')
        small_idx = 0
        n = 0
        for i, v in enumerate(unique_vals):
            if unused[starts[i]]:
                f_start = starts[i]
                f_end = f_start + run_lengths[i]
                t_start = small_idx
                t_end = small_idx + run_lengths[i]
                self.small_objs[t_start:t_end] = sorted_objs[f_start:f_end]
                self.small_starts[n] = small_idx
                self.small_lengths[n] = run_lengths[i]
                self.small_vals_to_pos[v] = n
                n += 1
                small_idx += run_lengths[i]
        self.small_ids = np.fromiter((id(obj) for obj in self.small_objs), dtype='int64')
        self.small_sort_order = np.argsort(self.small_ids)
        """

    def get(self, val) -> ArrayPair:
        if val in self.big_vals:
            print(val, self.big_vals[val])
            return self.big_vals[val]
        else:
            # TODO ugh damn you can't actually bisect on val because it may not be comparable
            # gotta do, what, hashes instead? and scan for when the hash changes? yeah
            i = bisect_left(self.sm_unique_vals, val)
            if i >= len(self.sm_unique_vals) or self.sm_unique_vals[i] != val:
                print(i, self.sm_unique_vals[i])
                print(val, self.sm_unique_vals)
                raise KeyError('not in here')
            start = self.sm_starts[i]
            end = self.sm_starts[i] + self.sm_run_lengths[i]
            return make_array_pair(self.sm_objs[start:end])

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
