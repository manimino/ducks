from sortedcontainers import SortedDict
from typing import Callable, Union, Dict, Any, List

from cykhash import Int64Set, Int64toInt64Map

from hashindex.constants import SIZE_THRESH, HASH_MIN, HASH_MAX
from hashindex.init_helpers import BucketPlan, empty_plan
from hashindex.mutable_buckets import HashBucket, DictBucket
from hashindex.utils import get_field


def fill_in_gaps(bucket_plans: List[BucketPlan]) -> List[BucketPlan]:
    # TODO, sigh
    """
    The planned buckets must meet the requirements:
    1. A bucket must start at HASH_MIN
    2. Every DictBucket must have a bucket starting at its val_hash+1.
    """
    """
    fixed_plans = []
    if min(bucket_plans[0].distinct_hashes) != HASH_MIN:
        if len(bucket_plans[0].obj_arr) > SIZE_THRESH:
            # create an empty HashBucket left of this DictBucket
            fixed_plans.append()
        else:
            # extend the leftmost HashBucket to the left
            pass
    """
    return bucket_plans


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
        self.buckets = SortedDict()
        if bucket_plans:
            self._apply_bucket_plan(bucket_plans)
        else:
            # create a single HashBucket to cover the whole range.
            self.buckets[HASH_MIN] = HashBucket()

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
            db = DictBucket(
                list(hb.val_hash_counts.keys())[0],
                hb_objs,
                hb.obj_ids,
                None,
                self.field,
            )
            del self.buckets[k]
            self.buckets[db.val_hash] = db
        else:
            # split it into two hashbuckets
            new_hash_counts, new_obj_ids = self.buckets[k].split(
                self.field, self.obj_map
            )
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

        if (
            isinstance(self.buckets[k], HashBucket)
            and len(self.buckets[k]) > SIZE_THRESH
        ):
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

    def _remove_bucket(self, bucket_key: int):
        """
        Remove a bucket.

        If this creates a gap in the [HASH_MIN..HASH_MAX] space that is not covered by a bucket, fix that.
        """
        left_key, right_key = self._get_neighbors(bucket_key)
        if left_key is not None and isinstance(self.buckets[left_key], HashBucket):
            # Case 1: There is a hash bucket to the left.
            # Just delete this bucket; the gap is covered.
            del self.buckets[bucket_key]
        else:
            # Case 2: The left neighbor is nonexistent, or is a DictBucket. Let's look right.
            if right_key is not None and isinstance(right_key, HashBucket):
                # Case 2a. The right neighbor is a hash bucket. We can expand it leftwards to cover the gap.
                self.buckets[bucket_key] = self.buckets[right_key]
                del self.buckets[right_key]
                del self.buckets[bucket_key]
            else:
                # Case 2b. The right neighbor is nonexistent, or is a DictBucket.
                # Deletion of this bucket is not allowed, even if empty.
                pass

    def bucket_report(self):
        ls = []
        for bkey in self.buckets:
            bucket = self.buckets[bkey]
            bset = set()
            for obj_id in bucket.get_all_ids():
                obj = self.obj_map.get(obj_id)
                bset.add(get_field(obj, self.field))
            ls.append((type(self.buckets[bkey]).__name__, bkey, "size:", len(bucket)))
        return ls

    def _add_bucket(self, hash_pos, bp: BucketPlan):
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
        self.buckets[hash_pos] = b

    def _apply_bucket_plan(self, bucket_plans: List[BucketPlan]):
        """
        Creates all buckets in bucket_plans.

        Fills any gaps in the plans by adding or expanding HashBuckets. That ensures every possible int between
        MIN_HASH and MAX_HASH is covered by exactly 1 bucket, with no gaps.
        """
        next_needed = HASH_MIN
        for b in bucket_plans:
            print(b)
            mh = b.distinct_hashes[0]
            btype = 'd' if sum(b.distinct_hash_counts) > SIZE_THRESH else 'h'
            # resolve any gaps
            if next_needed is not None and mh > next_needed:
                if btype == 'h':
                    # expand this bucket to the left
                    mh = next_needed
                else:  # btype == 'd'
                    # this is a dictbucket; add a hashbucket to fill the empty space
                    self._add_bucket(next_needed, empty_plan())
            # add this bucket
            self._add_bucket(mh, b)
            if btype == 'd' and mh < HASH_MAX:
                next_needed = mh + 1
            else:
                next_needed = None
        # handle final gap, if needed
        if next_needed is not None:
            self._add_bucket(next_needed, empty_plan())

    def _get_neighbors(self, bucket_key):
        try:
            left_idx = self.buckets.bisect_left(bucket_key-1)
            left_key, _ = self.buckets.peekitem(left_idx)
        except IndexError:
            left_key = None
        try:
            right_idx = self.buckets.bisect_right(bucket_key)
            right_key, _ = self.buckets.peekitem(right_idx)
        except IndexError:
            right_key = None
        return left_key, right_key
