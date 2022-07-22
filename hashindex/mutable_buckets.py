from typing import Dict, Any, Union, Iterable, Callable, Optional, Tuple

from cykhash import Int64Set

from hashindex.utils import get_field

from hashindex.exceptions import StaleObjectRemovalError


class HashBucket:
    """
    A HashBucket contains all obj_ids that have value hashes between some min and max value.
    When the number of items in a HashBucket reaches SIZE_THRESH, the bucket will be split
    into two buckets.
    """

    def __init__(
        self, obj_ids: Int64Set = None
    ):
        self.obj_ids = obj_ids if obj_ids else Int64Set()

    def add(self, obj_id):
        self.obj_ids.add(obj_id)

    def get_all_ids(self):
        return self.obj_ids

    def remove(self, _, obj_id):
        self.obj_ids.remove(obj_id)

    def dump_some_out_maybe(self, field, obj_map: Dict[int, Any]) -> Tuple[Optional[Int64Set],
                                                                           Optional[int],
                                                                           Optional[Dict[int, Int64Set]]]:
        """
        When a hashbucket is overfilled, dump some out maybe.

        Or maybe we only have 1 unique hash, and this should be a dictbucket.
        Returns (dumped_ids, None) or (None, dict_for_a_dict_bucket), depending.
        """
        val_to_obj_ids = dict()
        val_hash_to_obj_ids = dict()
        for obj_id in self.obj_ids:
            val = get_field(obj_map[obj_id], field)
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
            return None, None, val_to_obj_ids

        my_hashes = list(sorted(val_hash_to_obj_ids.keys()))

        # dump out the upper half the hash values
        half_point = len(my_hashes) // 2

        # dereference each object
        # Find the objects with field_vals that hash to any of dumped_hashes
        # we will move their ids to the new bucket
        dumped_obj_ids = Int64Set()
        for val_hash in my_hashes[half_point:]:
            for obj_id in val_hash_to_obj_ids[val_hash]:
                dumped_obj_ids.add(obj_id)
                self.obj_ids.remove(obj_id)
        return dumped_obj_ids, my_hashes[half_point], None

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

    def __init__(
        self,
        val_hash: int,
        objs: Iterable[Any],
        obj_ids: Iterable[int],
        vals: Iterable[Any],
        field: Union[str, Callable],
    ):
        self.val_hash = val_hash
        self.d = dict()
        for i, obj_id in enumerate(obj_ids):
            obj = objs[i]
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
                "Cannot remove object (not found). Object was changed without using update()."
            )
        self.d[val].remove(obj_id)
        if len(self.d[val]) == 0:
            del self.d[val]

    def get_matching_ids(self, val):
        if val in self.d:
            return self.d[val]
        else:
            # Happens in the extremely rare case where an object's field is changed to a different
            # value that has the same hash.
            return Int64Set()

    def __len__(self):
        return sum(len(s) for s in self.d.values())
