from sortedcontainers import SortedDict
from typing import Callable, Union, Dict, Any, List

from cykhash import Int64Set, Int64toInt64Map

from hashindex.constants import SIZE_THRESH, HASH_MIN, HASH_MAX
from hashindex.init_helpers import BucketPlan, empty_plan
from hashindex.mutable_buckets import HashBucket, DictBucket
from hashindex.mutable_bucket_manager import MutableBucketManager
from hashindex.utils import get_field


class MutableFieldIndex:
    """
    Stores the possible values of this field in a collection of buckets.
    Several values may be allocated to the same bucket for space efficiency reasons.
    """

    def __init__(
        self,
        field: Union[Callable, str],
        obj_map: Dict[int, Any],
        bucket_plans: List[BucketPlan] = None,
    ):
        self.field = field
        self.obj_map = obj_map
        self.mbm = MutableBucketManager()
        if bucket_plans:
            self._apply_bucket_plan(bucket_plans)
        else:
            # create a single HashBucket to cover the whole range.
            self.mbm[HASH_MIN] = HashBucket()

    def get_objs(self, val):
        val_hash = hash(val)
        k = self.mbm.get_bucket_key_for(val_hash)
        bucket = self.mbm[k]

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
        k = self.mbm.get_bucket_key_for(val_hash)
        bucket = self.mbm[k]

        if isinstance(bucket, DictBucket):
            try:
                return bucket.get_matching_ids(val)
            except KeyError as e:
                for ki in sorted(self.mbm):
                    if isinstance(self.mbm[ki], DictBucket):
                        print(ki, self.mbm[ki], list(self.mbm[ki].d.keys()), len(self.mbm[ki]))
                    else:
                        print(ki, self.mbm[ki])
                print('---', val, val_hash)
                raise e
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

    def _handle_big_hash_bucket(self, k):
        # A HashBucket is over threshold.
        # If it contains values that all hash to the same thing, make it a DictBucket.
        # If it has many val_hashes, split it into two HashBuckets.
        hb = self.mbm[k]
        if len(hb.val_hash_counts) == 1:
            # convert it to a dictbucket
            hb_objs = [self.obj_map[obj_id] for obj_id in hb.obj_ids]
            db = DictBucket(
                list(hb.val_hash_counts.keys())[0],
                hb_objs,
                hb.obj_ids,
                None,
                self.field,
            )
            self.mbm.remove_bucket(k)
            self.mbm[db.val_hash] = db
            # The HashBucket we removed previously spanned a range of hash values,
            # but the new DictBucket only covers 1 hash value. We may need to create HashBuckets on the
            # left and right sides.
            print('caller split')
            left_key, right_key = self.mbm.get_neighbors(k)
            if right_key is None or right_key > db.val_hash + 1:
                self.mbm[db.val_hash + 1] = HashBucket()
            if db.val_hash > HASH_MIN:
                if left_key is None:
                    self.mbm[HASH_MIN] = HashBucket()
                elif left_key < db.val_hash - 1 and isinstance(self.mbm[left_key], DictBucket):
                    self.mbm[HASH_MIN] = HashBucket
        else:
            # split it into two hashbuckets
            new_hash_counts, new_obj_ids = self.mbm[k].split(
                self.field, self.obj_map
            )
            new_bucket = HashBucket()
            new_bucket.update(new_hash_counts, new_obj_ids)
            self.mbm[min(new_hash_counts.keys())] = new_bucket

    def add(self, obj_id, obj):
        val = get_field(obj, self.field)
        val_hash = hash(val)
        k = self.mbm.get_bucket_key_for(val_hash)
        if isinstance(self.mbm[k], DictBucket):
            if val_hash == self.mbm[k].val_hash:
                # add to dictbucket
                self.mbm[k].add(val, obj_id)
            else:
                # can't put it in this dictbucket, the val_hash doesn't match.
                # Make a new hashbucket to hold this item.
                self.mbm[k + 1] = HashBucket()
                self.mbm[k + 1].add(val_hash, obj_id)
        else:
            # add to hashbucket
            self.mbm[k].add(val_hash, obj_id)

        if (
            isinstance(self.mbm[k], HashBucket)
            and len(self.mbm[k]) > SIZE_THRESH
        ):
            self._handle_big_hash_bucket(k)

    def remove(self, obj_id, obj):
        """
        Remove a single object from the index.

        If a bucket ever gets empty, remove it.
        """
        val = get_field(obj, self.field)
        val_hash = hash(val)
        k = self.mbm.get_bucket_key_for(val_hash)
        if isinstance(self.mbm[k], HashBucket):
            self.mbm[k].remove(val_hash, obj_id)
        else:
            self.mbm[k].remove(val, obj_id)
        if len(self.mbm[k]) == 0:
            self.mbm.remove_bucket(k)

    def bucket_report(self):
        ls = []
        for bkey in self.mbm:
            bucket = self.mbm[bkey]
            bset = set()
            for obj_id in bucket.get_all_ids():
                obj = self.obj_map.get(obj_id)
                bset.add(get_field(obj, self.field))
            ls.append((type(self.mbm[bkey]).__name__, bkey, "size:", len(bucket)))
        return ls

    def _add_plan_bucket(self, hash_pos: int, bp: BucketPlan):
        """Adds a bucket. Only used during init."""
        if len(bp.distinct_hash_counts) == 1 and bp.distinct_hash_counts[0] > SIZE_THRESH:
            bucket_obj_ids = [id(obj) for obj in bp.obj_arr]
            b = DictBucket(
                bp.distinct_hashes[0],
                bp.obj_arr,
                bucket_obj_ids,
                bp.val_arr,
                self.field,
            )
        else:
            bucket_obj_ids = Int64Set(id(obj) for obj in bp.obj_arr)
            val_hash_counts = Int64toInt64Map(
                zip(bp.distinct_hashes, bp.distinct_hash_counts)
            )
            b = HashBucket(bucket_obj_ids, val_hash_counts)
        self.mbm[hash_pos] = b

    def _apply_bucket_plan(self, bucket_plans: List[BucketPlan]):
        """
        Creates all buckets in bucket_plans.

        Fills any gaps in the plans by adding or expanding HashBuckets. That ensures every possible int between
        MIN_HASH and MAX_HASH is covered by exactly 1 bucket, with no gaps.
        """
        next_needed = HASH_MIN
        for b in bucket_plans:
            mh = b.distinct_hashes[0]
            btype = 'd' if sum(b.distinct_hash_counts) > SIZE_THRESH else 'h'
            # resolve any gaps
            if next_needed is not None and mh > next_needed:
                if btype == 'h':
                    # expand this bucket to the left
                    mh = next_needed
                else:
                    # this is a dictbucket; add a hashbucket to fill the empty space
                    self._add_plan_bucket(next_needed, empty_plan())
            # add this bucket
            self._add_plan_bucket(mh, b)
            if btype == 'd' and mh < HASH_MAX:
                next_needed = mh + 1
            else:
                next_needed = None
        # handle final gap, if any
        if next_needed is not None:
            self._add_plan_bucket(next_needed, empty_plan())
