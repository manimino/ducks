
from sortedcontainers import SortedDict
from typing import Callable, Union, Dict, Any, List

from cykhash import Int64Set, Int64toInt64Map

from hashindex.constants import SIZE_THRESH, HASH_MIN
from hashindex.init_helpers import BucketPlan
from hashindex.mutable_buckets import HashBucket, DictBucket
from hashindex.utils import get_field


class MutableFieldIndex:
    """
    Stores the possible values of this field in a collection of buckets.
    Several values may be allocated to the same bucket for space efficiency reasons.
    """

    def __init__(self,
                 field: Union[Callable, str],
                 obj_map: Dict[int, Any],
                 bucket_plans: List[BucketPlan] = None):
        self.field = field
        self.obj_map = obj_map
        self.buckets = SortedDict()  # O(1) add / remove, O(log(n)) find bucket for key
        self.buckets[HASH_MIN] = HashBucket()  # always contains at least one bucket
        if bucket_plans:
            for bp in bucket_plans:
                self._add_bucket(bp)

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
            # get everything in this HashBucket, and filter to just the obj_ids where val matches
            matched_ids = Int64Set()
            for obj_id in bucket.get_all_ids():
                obj = self.obj_map.get(obj_id)
                obj_val = get_field(obj, self.field)
                if obj_val is val or obj_val == val:
                    matched_ids.add(obj_id)
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
            hb_objs = [self.obj_map[obj_id] for obj_id in hb.obj_ids]
            db = DictBucket(list(hb.val_hash_counts.keys())[0], hb_objs, hb.obj_ids, None, self.field)
            del self.buckets[k]
            self.buckets[db.val_hash] = db
        else:
            # split it into two hashbuckets
            new_hash_counts, new_obj_ids = self.buckets[k].split(self.field, self.obj_map)
            new_bucket = HashBucket()
            new_bucket.update(new_hash_counts, new_obj_ids)
            self.buckets[min(new_hash_counts.keys())] = new_bucket

    def add(self, obj_id, obj):
        val = get_field(obj, self.field)
        val_hash = hash(val)
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

    def remove(self, obj_id, obj):
        """
        Remove a single object from the index.

        If a bucket ever gets empty, delete it unless it's the leftmost one.
        There will always be at least one bucket.
        TODO: What if a DictBucket is created on the min hash value?
        TODO: What if a DictBucket is removed, and the bucket to the right of it is a HashBucket?
        TODO: What if a DictBucket is removed, and the bucket to the right of it is another DictBucket?
        """
        val = get_field(obj, self.field)
        val_hash = hash(val)
        k = self._get_bucket_key_for(val_hash)
        if isinstance(self.buckets[k], HashBucket):
            self.buckets[k].remove(val_hash, obj_id)
        else:
            self.buckets[k].remove(val, obj_id)
        if len(self.buckets[k]) == 0:
            self._remove_bucket(k)

    def _remove_bucket(self, bucket_id: int):
        """
        Possible conditions:
        - This bucket is a HashBucket, and...
            - There is no bucket to the left of this one.
            - This bucket is between two DictBuckets.
            - This bucket has a DictBucket
        - This bucket is a DictBucket, and...
            - ugh
            - can't wait to work on the FrozenIndex where this isn't a thing
        """
        if bucket_id != HASH_MIN:
            # Never delete the leftmost nondict bucket.
            return
        del self.buckets[bucket_id]

    def _add_bucket(self, bp: BucketPlan):
        """Adds a bucket. Only used during init."""
        if len(bp.distinct_hash_counts) == 1 and bp.distinct_hash_counts > SIZE_THRESH:
            bucket_obj_ids = [id(obj) for obj in bp.obj_arr]
            b = DictBucket(bp.distinct_hashes[0],
                           bp.obj_arr,
                           bucket_obj_ids,
                           bp.val_arr,
                           self.field)
        else:
            bucket_obj_ids = Int64Set(id(obj) for obj in bp.obj_arr)
            val_hash_counts = Int64toInt64Map(zip(bp.distinct_hashes, bp.distinct_hash_counts))
            b = HashBucket(bucket_obj_ids, val_hash_counts)
        lowest_hash = min(bp.distinct_hashes)
        self.buckets[lowest_hash] = b

    def bucket_report(self):
        ls = []
        for bkey in self.buckets:
            bucket = self.buckets[bkey]
            bset = set()
            for obj_id in bucket.get_all_ids():
                obj = self.obj_map.get(obj_id)
                bset.add(get_field(obj, self.field))
            ls.append((bkey, bset, 'size:', len(bucket), type(self.buckets[bkey]).__name__))
        return ls
