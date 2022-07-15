from typing import Optional, Any, Dict, Union, Callable, Iterable

import numpy as np
import sortednp as snp

from hashindex.constants import SIZE_THRESH
from hashindex.exceptions import MissingIndexError
from hashindex.frozen_field import FrozenFieldIndex
from hashindex.init_helpers import compute_buckets
from hashindex.utils import int_arr


class FrozenBlashIndex:
    def __init__(self,
                 objs: Optional[Iterable[Any]] = None,
                 on: Iterable[Union[str, Callable]] = None
                 ):
        """
        TODO: we may not actually need these arrays, since they can be read out of any field index.
        Consider removing.
        """
        self.id_arr = np.array([id(obj) for obj in objs], dtype="uint64")
        self.obj_arr = np.array(objs, dtype="O")
        self.on = on
        self.indices = {}
        for field in on:
            plan = compute_buckets(objs, field, SIZE_THRESH)
            self.indices[field] = FrozenFieldIndex(plan)

    def _dereference_obj_ids(self, sorted_obj_ids: np.array) -> np.ndarray:
        """Get the objs associated with many obj_ids. Assumes everything is sorted. Very fast."""
        result = snp.intersect(sorted_obj_ids, self.obj_ids, indices=True)
        # result format:
        # [matching_elements, [positions_in_first_array, positions_in_second_array]]
        # ref: https://pypi.org/project/sortednp/
        positions = result[1][1]
        return self.objects[positions]

    def find(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> np.ndarray:
        return self._dereference_obj_ids(self.find_obj_ids(match, exclude))

    def find_obj_ids(
        self,
        match: Optional[Dict[str, Any]] = None,
        exclude: Optional[Dict[str, Any]] = None,
    ) -> np.ndarray:
        # input validation -- check that we have an index for all desired lookups
        required_indices = set()
        if match:
            required_indices.update(match.keys())
        if exclude:
            required_indices.update(exclude.keys())
        missing_indices = required_indices.difference(self.indices)
        if missing_indices:
            raise MissingIndexError

        # perform 'match' query
        if match:
            # find intersection of each field
            arrs = [self._match_any_of(field, value) for field, value in match.items()]
            hits = snp.kway_intersect(*arrs, assume_sorted=True)
        else:
            # 'match' is unspecified, so match all objects
            hits = self.obj_ids

        # perform 'exclude' query
        if exclude:
            for field, value in exclude.items():
                field_hits = self._match_any_of(field, value)
                # sortednp doesn't implement difference, so np.setdiff1d is the best we can do.
                hits = np.setdiff1d(hits, field_hits, assume_unique=True)
                if len(hits) == 0:
                    break
        return hits

    def _match_any_of(self, field: str, value: Any) -> np.ndarray:
        """Get matches during a find(). If multiple values specified, handle union logic."""
        if type(value) is list:
            # take the union of all matches
            match_arrays = [self.indices[field].get(v, int_arr()) for v in value]
            # sortednp's docs say to try heapq.merge and other numpy functions, but snp.kway_merge
            # is actually 2x ~ 10x faster than any of those.
            return snp.kway_merge(
                *match_arrays, assume_sorted=True, duplicates=snp.DROP
            )
        else:
            return self.indices[field].get(value, int_arr())

    def _find_obj_id(self, ptr):
        """Use binary search to look up the position of an obj id in the sorted numpy array."""
        i = self.obj_ids.searchsorted(ptr)
        if i == len(self.obj_ids):
            # happens when index is empty, or the ptr is bigger than any obj ptr we have
            return -1
        # searchsorted tells us the first index <= target, check for ==
        if self.obj_ids.values[i] == ptr:
            return i
        return -1

    def __contains__(self, obj):
        return self._find_obj_id(id(obj)) != -1

    def __iter__(self):
        return iter(self.objects)
