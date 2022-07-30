import numpy as np

from bisect import bisect_left
from collections.abc import Hashable
from typing import Optional, Any, Dict, Union, Callable, Iterable, List

import sortednp as snp

from hashbox.frozen.frozen_attr import FrozenFieldIndex
from hashbox.frozen.utils import make_empty_int_array, snp_difference
from hashbox.utils import validate_query


class FrozenHashBox:
    """A much faster HashBox that lacks the ability to add or remove objects."""

    def __init__(self, objs: Iterable[Any], on: Iterable[Union[str, Callable]]):
        """Create a FrozenHashBox containing the objs, queryable by the 'on' attributes.

        Args:
            objs (Any iterable containing any types): The objects that FrozenHashBox will contain.
                Must contain at least one object. Objects do not need to be hashable, any object works.

            on (Iterable of attributes): The attributes that FrozenHashBox will build indices on.
                Must contain at least one.

        Objects in obj do not need to have all of the attributes in 'on'. Objects will be considered to have a
        None value for missing attributes.
        """
        if not objs:
            raise ValueError(
                "Cannot build an empty FrozenHashBox; at least 1 object is required."
            )
        self.on = on
        self.indices = {}

        self.obj_arr = np.empty(len(objs), dtype="O")
        for i, obj in enumerate(objs):
            self.obj_arr[i] = obj
        self.id_arr = np.fromiter((id(obj) for obj in self.obj_arr), dtype="int64")
        # sort both arrays by obj_id
        sort_order = np.argsort(self.id_arr)
        self.id_arr = self.id_arr[sort_order]
        self.obj_arr = self.obj_arr[sort_order]

        for field in on:
            self.indices[field] = FrozenFieldIndex(field, self.obj_arr)

    def find(
        self,
        match: Optional[
            Dict[Union[str, Callable], Union[Hashable, List[Hashable]]]
        ] = None,
        exclude: Optional[
            Dict[Union[str, Callable], Union[Hashable, List[Hashable]]]
        ] = None,
    ) -> np.ndarray:
        """Find objects in the FrozenHashBox that satisfy the match and exclude constraints.

        Args:
            match (Dict of {attribute: value}, or None): Specifies the subset of objects that match.
                Attribute is a string or Callable. Must be one of the attributes specified in the constructor.
                Value is any hashable type, or it can be a list of values.

                There is an implicit "and" between elements.
                Example: match={'a': 1, 'b': 2} matches all objects with 'a'==1 and 'b'==2.

                When the value is a list, all objects containing any value in the list will match.
                Example: {'a': [1, 2, 3]} matches any object with an 'a' of 1, 2, or 3.

                If an attribute value is None, objects that are missing the attribute will be matched, as well as
                any objects that have the attribute equal to None.

                match=None means all objects will be matched.

            exclude (Dict of {attribute: value}, or None): Specifies the subset of objects that do not match.
                exclude={'a': 1, 'b': 2} ensures that no objects with 'a'==1 will be in the output, and no
                objects with 'b'==2 will be in the output.

                You can also read this as "a != 1 and b != 2".

                exclude={'a': [1, 2, 3]} ensures that no objects with 'a' equal to 1, 2, or 3 will be in the output.

        Returns:
            Numpy array of objects matching the constraints.

        Example:
            find(
                match={'a': 1, 'b': [1, 2, 3]},
                exclude={'c': 1, 'd': 1}
            )
            This is analogous to:
            filter(
                lambda obj: obj.a == 1 and obj.b in [1, 2, 3] and obj.c != 1 and obj.d != 1,
                objects
            )
        """

        validate_query(self.indices, match, exclude)

        # perform 'match' query
        hits = None
        if match:
            # find intersection of each field
            for field, value in match.items():
                # if multiple values for a field, find each value and union those first
                field_hits = self._match_any_of(field, value)
                if hits is None:  # this is the first field
                    hits = field_hits
                elif len(field_hits):
                    # intersect this field's hits with our hits so far
                    hits = snp.intersect(hits, field_hits)
                else:
                    # this field had no matches, therefore the intersection will be empty. We can stop here.
                    return np.empty(0, dtype="O")
        else:
            # 'match' is unspecified, so match all objects
            hits = self.id_arr

        # perform 'exclude' query
        if exclude:
            for field, value in exclude.items():
                field_hits = self._match_any_of(field, value)
                hits = snp_difference(hits, field_hits)

                if len(hits) == 0:
                    break

        return self._get_objs_by_ids(hits)

    def _match_any_of(
        self, field: Union[str, Callable], value: Union[Hashable, List[Hashable]]
    ) -> np.ndarray:
        """Get matches for a single field during a find(). If multiple values specified, handle union logic.

        Args:
            field: The attribute being queried.
            value: The value of the field to match, or if list, multiple values to match.

        Returns:
            Sorted array of object IDs.
        """
        if isinstance(value, list):
            # take the union of all matches
            matches = [self.indices[field].get(v) for v in value]
            # note: merging sorted arrays is often done with heapq, but heapq performs much slower here.
            # order bound ain't everything.
            matches = snp.kway_merge(*matches, assume_sorted=True)
            return matches
        else:
            return self.indices[field].get(value)

    def _get_objs_by_ids(self, id_arr: np.ndarray):
        _, indices = snp.intersect(id_arr, self.id_arr, indices=True)
        return self.obj_arr[indices[1]]

    def __contains__(self, obj):
        obj_id = id(obj)
        idx = bisect_left(self.id_arr, obj_id)
        if idx < 0 or idx >= len(self.id_arr):
            return False
        return self.id_arr[idx] == obj_id

    def __iter__(self):
        return iter(self.obj_arr)

    def __len__(self):
        return len(self.obj_arr)
