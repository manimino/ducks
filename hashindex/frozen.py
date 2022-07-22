from typing import Optional, Any, Dict, Union, Callable, Iterable

import numpy as np
from hashindex.constants import SIZE_THRESH
from hashindex.frozen_field import FrozenFieldIndex
from hashindex.init_helpers import compute_buckets
from hashindex.frozen_buckets import ArrayPair, empty_array_pair
from hashindex.utils import validate_query


class FrozenHashIndex:
    def __init__(self, objs: Iterable[Any], on: Iterable[Union[str, Callable]] = None):
        if not objs:
            raise ValueError(
                "Cannot build an empty FrozenHashIndex; at least 1 object is required."
            )
        if not on:
            raise ValueError("Need at least one field to index on.")
        self.on = on
        self.indices = {}
        for field in on:
            bucket_plans = compute_buckets(objs, field, SIZE_THRESH)
            self.indices[field] = FrozenFieldIndex(field, bucket_plans)

    def find(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> np.ndarray:
        return self._do_find(match, exclude).obj_arr

    def find_ids(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> np.ndarray:
        return self._do_find(match, exclude).id_arr

    def _do_find(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> ArrayPair:
        validate_query(self.indices, match, exclude)

        # perform 'match' query
        hits = None
        if match:
            # find intersection of each field
            for field, value in match.items():
                # if multiple values for a field, find each value and union those first
                field_hits = self._match_any_of(field, value)
                if hits is None:  # first field
                    hits = field_hits
                if field_hits:
                    # intersect this field's hits with our hits so far
                    hits.apply_intersection(field_hits)
                else:
                    # this field had no matches, therefore the intersection will be empty. We can stop here.
                    return empty_array_pair()
        else:
            # 'match' is unspecified, so match all objects
            hits = self._get_all()

        # perform 'exclude' query
        if exclude:
            for field, value in exclude.items():
                field_hits = self._match_any_of(field, value)
                hits.apply_difference(field_hits)
                if len(hits) == 0:
                    break

        return hits

    def _match_any_of(self, field: str, value: Any) -> ArrayPair:
        """Get matches for a single field during a find(). If multiple values specified, handle union logic."""
        if isinstance(value, list):
            # take the union of all matches
            matches = None
            for v in value:
                v_matches = self.indices[field].get(v)
                if matches is None:
                    matches = v_matches
                else:
                    matches.apply_union(v_matches)
            return matches
        else:
            return self.indices[field].get(value)

    def _get_all(self) -> ArrayPair:
        for f in self.indices:
            return self.indices[f].get_all()

    def __contains__(self, obj):
        for idx in self.indices.values():
            return obj in idx

    def __iter__(self):
        for idx in self.indices.values():
            return iter(idx)

    def __len__(self):
        for idx in self.indices.values():
            return len(idx)
