import numpy as np

from hashindex.frozen.array_pair import ArrayPair, make_array_pair, make_empty_array_pair
from typing import Union, Callable, Iterable, Any
from hashindex.init_helpers import sort_by_hash, group_by_val, run_length_encode
from hashindex.constants import SIZE_THRESH


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
        for i, v in enumerate(unique_vals):
            if run_lengths[i] > SIZE_THRESH:
                start = starts[i]
                end = start + run_lengths[i]
                obj_arr = sorted_objs[start:end]
                self.big_vals[v], _ = make_array_pair(obj_arr)
                unused[start:end] = False

        # Vals with few objs go in small_vals, which is a single array sorted by val.
        # We'll create id-sorted ArrayPairs from it on demand.
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
                print(t_start, t_end, f_start, f_end, len(self.small_objs))
                self.small_objs[t_start:t_end] = sorted_objs[f_start:f_end]
                self.small_starts[n] = small_idx
                self.small_lengths[n] = run_lengths[i]
                self.small_vals_to_pos[v] = n
                n += 1
                small_idx += run_lengths[i]

    def get(self, val) -> ArrayPair:
        if val in self.big_vals:
            print(val, self.big_vals[val])
            return self.big_vals[val]
        elif val in self.small_vals_to_pos:
            pos = self.small_vals_to_pos[val]
            start = self.small_starts[pos]
            end = self.small_starts[pos] + self.small_lengths[pos]
            ap, _ = make_array_pair(self.small_objs[start:end])
            print(ap)
            return ap

    def get_obj_ids(self, val) -> np.ndarray:
        return self.get(val).id_arr

    def get_all(self) -> ArrayPair:
        print('in ur get_all')
        arrs = make_empty_array_pair()
        for v in self.big_vals:
            arrs.apply_union(self.big_vals[v])
        small, _ = make_array_pair(self.small_objs)
        arrs.apply_union(small)
        return arrs

    def __iter__(self):
        return iter(self.objs)

    def __len__(self):
        return len(self.objs)

