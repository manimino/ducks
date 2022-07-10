import numpy as np
import sortednp as snp
from dataclasses import dataclass

from hashindex.init_helpers import BucketPlan


@dataclass
class TwoArrays:
    id_arr: np.ndarray
    obj_arr: np.ndarray

    def intersect(self, other):
        pass

    def union(self, other):
        pass

    def difference(self, other):
        pass


class HashBucket:
    def __init__(self, bi: BucketPlan):
        pass


class DictBucket:

    def __init__(self, bi: BucketPlan):
        pass

