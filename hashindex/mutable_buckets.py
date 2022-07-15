from typing import Dict, Any, Union, Iterable, Callable, Optional

from cykhash import Int64Set, Int64toInt64Map

from hashindex.utils import get_field


class HashBucket:
    """
    A HashBucket contains all obj_ids that have value hashes between some min and max value.
    When the number of items in a HashBucket reaches SIZE_THRESH, the bucket will be split
    into two buckets.
    """

    def __init__(self, obj_ids: Int64Set = None, val_hash_counts: Int64toInt64Map = None):
        self.obj_ids = obj_ids if obj_ids else Int64Set()
        self.val_hash_counts = val_hash_counts if val_hash_counts else Int64toInt64Map()

    def add(self, val_hash, obj_id):
        count = self.val_hash_counts.get(val_hash, 0)
        self.val_hash_counts[val_hash] = count + 1
        self.obj_ids.add(obj_id)

    def update(self, new_val_hash_counts, new_obj_ids):
        for v, c in new_val_hash_counts.items():
            count = self.val_hash_counts.get(v, 0)
            self.val_hash_counts[v] = count + c
        self.obj_ids = self.obj_ids.union(new_obj_ids)

    def get_all_ids(self):
        return self.obj_ids

    def remove(self, val_hash, obj_id):
        # todo handle exceptions
        self.val_hash_counts[val_hash] -= 1
        self.obj_ids.remove(obj_id)

    def split(self, field, obj_map: Dict[int, Any]):
        my_hashes = list(sorted(self.val_hash_counts.keys()))
        # dump out the upper half of our hashes
        half_point = len(my_hashes) // 2
        dumped_hash_counts = {v: self.val_hash_counts[v] for v in my_hashes[half_point:]}

        # dereference each object
        # Find the objects with field_vals that hash to any of dumped_hashes
        # we will move their ids to the new bucket
        dumped_obj_ids = Int64Set()
        for obj_id in list(self.obj_ids):
            obj = obj_map.get(obj_id)
            obj_val = getattr(obj, field, None)
            if hash(obj_val) in dumped_hash_counts:
                dumped_obj_ids.add(obj_id)
                self.obj_ids.remove(obj_id)
        for dh in dumped_hash_counts:
            del self.val_hash_counts[dh]
        return dumped_hash_counts, dumped_obj_ids

    def __len__(self):
        return len(self.obj_ids)


class DictBucket:
    """
    A DictBucket stores object ids corresponding to only one val_hash. Note that multiple values
    could have the same val_hash (collision), but usually this bucket will contain just one value.
    It stores all entries in a dict of {val: obj_id_set}, so it supports lookup by field value.
    This makes finding objects by val very fast. Unlike a HashBucket, we don't have to dereference
    all the objects and check their values during a find().
    DictBucket is great when many objects have the same val.
    """

    def __init__(self,
                 val_hash: int,
                 objs: Iterable[Any],
                 obj_ids: Iterable[int],
                 vals: Optional[Iterable[Any]],
                 field: Union[str, Callable]):
        self.val_hash = val_hash
        self.d = dict()
        for i, obj_id in enumerate(obj_ids):
            obj = objs[i]
            if vals is not None:
                val = vals[i]
            else:
                val = get_field(obj, field)
            if val not in self.d:
                self.d[val] = Int64Set()
            self.d[val].add(obj_id)

    def add(self, val, obj_id):
        obj_ids = self.d.get(val, Int64Set())
        obj_ids.add(obj_id)

    def remove(self, val, obj_id):
        if val not in self.d:
            raise KeyError('Object value not in here')
        if obj_id not in self.d[val]:
            raise KeyError('Object ID not in here')
        self.d[val].remove(obj_id)
        if len(self.d[val]) == 0:
            del self.d[val]

    def get_matching_ids(self, val):
        return self.d[val]

    def get_all_ids(self):
        return Int64Set.union(*self.d.values())

    def __len__(self):
        return sum(len(s) for s in self.d.values())
