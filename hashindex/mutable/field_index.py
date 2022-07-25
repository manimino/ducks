from typing import Callable, Union, Dict, Any, List

from cykhash import Int64Set

from hashindex.constants import SIZE_THRESH, HASH_MIN, HASH_MAX
from hashindex.init_helpers import BucketPlan, empty_plan
from hashindex.mutable.buckets import HashBucket, DictBucket
from hashindex.mutable.bucket_manager import MutableBucketManager
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

    def get_obj_ids(self, val):
        val_hash = hash(val)
        k = self.mbm.get_bucket_key_for(val_hash)
        bucket = self.mbm[k]
        return bucket.get_matching_ids(val)

    def add(self, obj_id, obj):
        val = get_field(obj, self.field)
        val_hash = hash(val)
        k = self.mbm.get_bucket_key_for(val_hash)
        self.mbm[k].add(val, obj_id)
        if isinstance(self.mbm[k], HashBucket) and len(self.mbm[k]) > SIZE_THRESH:
            self.mbm.handle_big_hash_bucket(k)

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

    def _add_plan_bucket(self, hash_pos: int, bp: BucketPlan):
        """Adds a bucket. Only used during init."""
        bucket_obj_ids = [id(obj) for obj in bp.obj_arr]
        if (
            len(bp.distinct_hash_counts) == 1
            and bp.distinct_hash_counts[0] > SIZE_THRESH
        ):
            b = DictBucket(
                bp.distinct_hashes[0],
                bp.obj_arr,
                bucket_obj_ids,
                bp.val_arr
            )
        else:
            b = HashBucket(bp.val_arr, bucket_obj_ids)
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
            btype = "d" if sum(b.distinct_hash_counts) > SIZE_THRESH else "h"
            # resolve any gaps
            if next_needed is not None and mh > next_needed:
                if btype == "h":
                    # expand this bucket to the left
                    mh = next_needed
                else:
                    # this is a dictbucket; add a hashbucket to fill the empty space
                    self._add_plan_bucket(next_needed, empty_plan())
            # add this bucket
            self._add_plan_bucket(mh, b)
            if btype == "d" and mh < HASH_MAX:
                next_needed = mh + 1
            else:
                next_needed = None
        # handle final gap, if any
        if next_needed is not None:
            self._add_plan_bucket(next_needed, empty_plan())
