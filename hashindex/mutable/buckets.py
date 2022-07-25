from typing import Dict, Any, Union, Iterable, Callable, Optional, Tuple, List

from cykhash import Int64Set

from hashindex.exceptions import StaleObjectRemovalError


class HashBucket:
    """
    A HashBucket contains all obj_ids that have value hashes between some min and max value.
    When the number of items in a HashBucket reaches SIZE_THRESH, the bucket will be split
    into two buckets.
    """

    def __init__(
        self, vals = None, obj_ids: Int64Set = None
    ):
        self.obj_id_vals = dict(zip(obj_ids, vals)) if obj_ids else dict()

    def add(self, val, obj_id):
        self.obj_id_vals[obj_id] = val

    def get_matching_ids(self, val):
        """Get the obj_ids where val matches"""
        matched_ids = Int64Set()
        for obj_id, obj_val in self.obj_id_vals.items():
            if obj_val is val or obj_val == val:
                matched_ids.add(obj_id)
        return matched_ids

    def remove(self, _, obj_id):
        del self.obj_id_vals[obj_id]

    def dump_some_out_maybe(self) -> Tuple[Optional[List],
                                           Optional[List],
                                           Optional[int],
                                           Optional[Dict[int, Int64Set]]]:
        # TODO this function is a tire fire, plz refactor
        """
        When a hashbucket is overfilled, dump some out maybe.

        Or maybe we only have 1 unique hash, and this should be a dictbucket.
        Returns (dumped_ids, None) or (None, dict_for_a_dict_bucket), depending.
        """
        val_to_obj_ids = dict()
        val_hash_to_obj_ids = dict()
        for obj_id in self.obj_id_vals:
            val = self.obj_id_vals[obj_id]
            if len(val_hash_to_obj_ids) < 2:
                # add to val dict, as long as we still think this might become a DictBucket
                if val not in val_to_obj_ids:
                    val_to_obj_ids[val] = Int64Set()
                val_to_obj_ids[val].add(obj_id)
            # add to val_hash dict
            val_hash = hash(val)
            if val_hash not in val_hash_to_obj_ids:
                val_hash_to_obj_ids[val_hash] = Int64Set()
            val_hash_to_obj_ids[val_hash].add(obj_id)

        if len(val_hash_to_obj_ids) == 1:
            # looks like a dictbucket
            return None, None, None, val_to_obj_ids

        my_hashes = list(sorted(val_hash_to_obj_ids.keys()))

        # dump out the upper half the hash values
        half_point = len(my_hashes) // 2

        # we will move their ids and vals to the new bucket
        dumped_obj_ids = []
        dumped_vals = []
        for val_hash in my_hashes[half_point:]:
            for obj_id in val_hash_to_obj_ids[val_hash]:
                dumped_obj_ids.append(obj_id)
                dumped_vals.append(self.obj_id_vals[obj_id])
                del self.obj_id_vals[obj_id]
        return dumped_obj_ids, dumped_vals, my_hashes[half_point], None

    def __len__(self):
        return len(self.obj_id_vals)


class DictBucket:
    """
    A DictBucket stores object ids corresponding to only one val_hash. Note that multiple values
    could have the same val_hash (collision), but usually this bucket will contain just one value.
    It stores all entries in a dict of {val: obj_id_set}, so it supports lookup by field value.
    This makes finding objects by val very fast. Unlike a HashBucket, we don't have to dereference
    all the objects and check their values during a find().
    DictBucket is great when many objects have the same val.
    """

    def __init__(
        self,
        val_hash: int,
        objs: Iterable[Any],
        obj_ids: Iterable[int],
        vals: Iterable[Any],
    ):
        self.val_hash = val_hash
        self.d = dict()
        for i, obj_id in enumerate(obj_ids):
            val = vals[i]
            if val not in self.d:
                self.d[val] = Int64Set()
            self.d[val].add(obj_id)

    def add(self, val, obj_id):
        obj_ids = self.d.get(val, Int64Set())
        obj_ids.add(obj_id)

    def remove(self, val, obj_id):
        if val not in self.d or obj_id not in self.d[val]:
            raise StaleObjectRemovalError(
                "Cannot remove object (not found)."
            )
        self.d[val].remove(obj_id)
        if len(self.d[val]) == 0:
            del self.d[val]

    def get_matching_ids(self, val):
        if val in self.d:
            return self.d[val]

    def __len__(self):
        return sum(len(s) for s in self.d.values())
