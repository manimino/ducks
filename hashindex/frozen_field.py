from hashindex.init_helpers import BucketPlan
from hashindex.exceptions import FrozenError

class FrozenFieldIndex:

    def __init__(self, bucket_plans: BucketPlan):
        for bucket_plan in bucket_plans:
            self._add_bucket(bp)



    def add(self):
        raise FrozenError('Cannot add items to a FrozenHashIndex. If mutability is needed, try HashIndex instead.')

    def remove(self):
        raise FrozenError('Cannot remove items from a FrozenHashIndex. If mutability is needed, try HashIndex instead.')

    def update(self):
        raise FrozenError('Cannot update items in a FrozenHashIndex. If mutability is needed, try HashIndex instead.')
