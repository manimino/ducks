
from sortedcontainers import SortedDict
from typing import Callable, Union, Dict, Any

from hashindex.constants import SIZE_THRESH, HASH_MIN
from hashindex.mutable_buckets import HashBucket, DictBucket


class MutableFieldIndex:
    """
    Stores the possible values of this field in a collection of buckets.
    Several values may be allocated to the same bucket for space efficiency reasons.
    """

    def __init__(self, field: Union[Callable, str], obj_map: Dict[int, Any]):
        self.buckets = SortedDict()  # O(1) add / remove, O(log(n)) find bucket for key
        self.buckets[HASH_MIN] = HashBucket()  # always contains at least one bucket
        self.obj_map = obj_map  # for reading only, will not be mutated here
        self.field = field

    def get_objs(self, val):
        val_hash = hash(val)
        k = self._get_bucket_key_for(val_hash)
        bucket = self.buckets[k]

        if isinstance(bucket, DictBucket):
            return [self.obj_map.get(obj_id) for obj_id in bucket.get_matching_ids(val)]
        else:
            # filter to just the objs that match val
            matched_objs = []
            for obj_id in bucket.get_all_ids():
                obj = self.obj_map.get(obj_id)
                obj_val = getattr(obj, self.field, None)
                if obj_val is val or obj_val == val:
                    matched_objs.append(obj)
            return matched_objs

    def get_obj_ids(self, val):
        val_hash = hash(val)
        k = self._get_bucket_key_for(val_hash)
        bucket = self.buckets[k]

        if isinstance(bucket, DictBucket):
            return bucket.get_matching_ids(val)
        else:
            # filter to just the obj_ids that match val
            matched_ids = []
            for obj_id in bucket.get_all_ids():
                obj = self.obj_map.get(obj_id)
                obj_val = getattr(obj, self.field, None)
                if obj_val is val or obj_val == val:
                    matched_ids.append(obj)
            return matched_ids

    def get_all_objs(self):
        return list(self.obj_map.values())

    def _get_bucket_key_for(self, val_hash):
        list_idx = self.buckets.bisect_right(val_hash) - 1
        k, _ = self.buckets.peekitem(list_idx)
        return k

    def _handle_big_hash_bucket(self, k):
        # A HashBucket is over threshold.
        # If it contains values that all hash to the same thing, make it a DictBucket.
        # If it has many val_hashes, split it into two HashBuckets.
        hb = self.buckets[k]
        if len(hb.val_hash_counts) == 1:
            # convert it to a dictbucket
            db = DictBucket(list(hb.val_hash_counts.keys())[0], hb.obj_ids, self.obj_map, self.field)
            del self.buckets[k]
            self.buckets[db.val_hash] = db
        else:
            # split it into two hashbuckets
            new_hash_counts, new_obj_ids = self.buckets[k].split(self.field, self.obj_map)
            new_bucket = HashBucket()
            new_bucket.update(new_hash_counts, new_obj_ids)
            self.buckets[min(new_hash_counts.keys())] = new_bucket

    def add(self, obj):
        val = getattr(obj, self.field, None)
        val_hash = hash(val)
        obj_id = id(obj)
        self.obj_map.add(obj_id, obj)
        k = self._get_bucket_key_for(val_hash)
        if isinstance(self.buckets[k], DictBucket):
            if val_hash == self.buckets[k].val_hash:
                # add to dictbucket
                self.buckets[k].add(val, obj_id)
            else:
                # can't put it in this dictbucket, the val_hash doesn't match.
                # Make a new hashbucket to hold this item.
                self.buckets[k + 1] = HashBucket()
                self.buckets[k + 1].add(val_hash, obj_id)
        else:
            # add to hashbucket
            self.buckets[k].add(val_hash, obj_id)

        if isinstance(self.buckets[k], HashBucket) and len(self.buckets[k]) > SIZE_THRESH:
            self._handle_big_hash_bucket(k)

    def remove(self, val, obj_id):
        """
        Remove a single object from the index.

        If a bucket ever gets empty, delete it unless it's the leftmost one.
        There will always be at least one bucket.
        TODO: What if a DictBucket is created on the min hash value?
        TODO: We should remove it and create a HashBucket instead.
        TODO: also check logic to make sure we create a new hash bucket to the right of dictbucket
        """
        val_hash = hash(val)
        k = self._get_bucket_key_for(val_hash)
        if isinstance(self.buckets[k], HashBucket):
            self.buckets[k].remove(val_hash, obj_id)
        else:
            self.buckets[k].remove(val, obj_id)
        if len(self.buckets[k]) == 0 and k != HASH_MIN:
            del self.buckets[k]

    def bucket_report(self):
        ls = []
        for bkey in self.buckets:
            bucket = self.buckets[bkey]
            bset = set()
            for obj_id in bucket.get_all_ids():
                o = self.obj_map.get(obj_id)
                bset.add(getattr(o, self.field))
            ls.append((bkey, bset, len(bucket), type(self.buckets[bkey]).__name__))
        return ls
