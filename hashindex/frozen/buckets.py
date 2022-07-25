from hashindex.frozen.array_pair import ArrayPair, make_array_pair, make_empty_array_pair
from hashindex.init_helpers import BucketPlan
from typing import Callable, Union


class FHashBucket:
    def __init__(self, bp: BucketPlan, field: Union[str, Callable]):
        self.field = field
        self.array_pair, sort_order = make_array_pair(bp.obj_arr)
        self.vals = bp.val_arr[sort_order]

    def get(self, val):
        match_pos = []
        for i in range(len(self)):
            if self.vals[i] == val or self.vals[i] is val:
                match_pos.append(i)
        return ArrayPair(
            id_arr=self.array_pair.id_arr[match_pos],
            obj_arr=self.array_pair.obj_arr[match_pos],
        )

    def get_all(self):
        return self.array_pair

    def __len__(self):
        return len(self.array_pair)

    def __iter__(self):
        return FHashBucketIterator(self)


class FDictBucket:
    def __init__(self, bp: BucketPlan, field: Union[str, Callable]):
        self.field = field
        first = bp.val_arr[
            0
        ]  # assumption: bp will never be empty (true as long as bucket size limit >= 1)
        if all(val == first for val in bp.val_arr):
            # In the overwhelming majority of cases, val will be unique.
            ap, _ = make_array_pair(bp.obj_arr)
            self.d = {first: ap}
        else:
            # Building a dict requires hashing every value, so there's some time cost here (~1s per 1M items).
            # Maybe worse since, as we know, the value hashes collide.
            # We want to make self.d = {val: numpy object array} here. Make a dict of {val: [idx]} first.
            d_idx = dict()
            for i, val in enumerate(bp.val_arr):
                if val not in d_idx:
                    d_idx[val] = []
                d_idx[val].append(i)
            self.d = dict()
            for val in d_idx:
                self.d[val], _ = make_array_pair(bp.obj_arr[d_idx[val]])

    def get_all(self):
        arrs = make_empty_array_pair()
        for val in self.d:
            arrs.apply_union(self.d[val])
        return arrs

    def get(self, val):
        return self.d.get(val, make_empty_array_pair())

    def __len__(self):
        return sum(len(self.d[val]) for val in self.d)

    def __iter__(self):
        return FDictBucketIterator(self)


class FHashBucketIterator:
    def __init__(self, fhb: FHashBucket):
        self.arr = fhb.array_pair.obj_arr
        self.i = 0

    def __next__(self):
        if self.i == len(self.arr):
            raise StopIteration
        obj = self.arr[self.i]
        self.i += 1
        return obj


class FDictBucketIterator:
    def __init__(self, fdb: FDictBucket):
        self.arrs = list(
            arr_pair.obj_arr for arr_pair in fdb.d.values() if len(arr_pair) > 0
        )
        self.i = 0
        self.j = 0

    def __next__(self):
        try:
            if self.j == len(self.arrs[self.i]):
                self.i += 1
                self.j = 0
            obj = self.arrs[self.i][self.j]
            self.j += 1
            return obj
        except IndexError:
            raise StopIteration
