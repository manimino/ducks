from bisect import bisect_left
from collections.abc import Hashable
from typing import Optional, Any, Dict, Union, Callable, Iterable, List, Set

import numpy as np
import sortednp as snp

from hashbox import ANY
from hashbox.frozen.frozen_attr import FrozenAttrIndex
from hashbox.frozen.utils import snp_difference
from hashbox.utils import make_empty_array, validate_query


class FrozenHashBox:
    """A much faster HashBox that lacks the ability to add or remove objects."""

    def __init__(self, objs: Iterable[Any], on: Iterable[Union[str, Callable]]):
        """Create a FrozenHashBox containing the objs, queryable by the 'on' attributes.

        Args:
            objs: The objects that FrozenHashBox will contain.
                Objects do not need to be hashable, any object works.

            on: The attributes that FrozenHashBox will build indices on.
                Must contain at least one.

        It's OK if the objects in "objs" are missing some or all of the attributes in "on". They will still be
        stored, and can found with find(), e.g. when matching all objects or objects missing an attribute.

        For the objects that do contain the attributes on "on", those attribute values must be hashable.
        """
        if not objs:
            raise ValueError(
                "Cannot build an empty FrozenHashBox; at least 1 object is required."
            )
        if not on:
            raise ValueError("Need at least one attribute.")
        if isinstance(on, str):
            on = [on]
        self.indices = {}

        self.obj_arr = np.empty(len(objs), dtype="O")
        self.dtype = "uint32" if len(objs) < 2 ** 32 else "uint64"
        for i, obj in enumerate(objs):
            self.obj_arr[i] = obj

        for attr in on:
            self.indices[attr] = FrozenAttrIndex(attr, self.obj_arr, self.dtype)

        self.sorted_obj_ids = np.sort(
            [id(obj) for obj in self.obj_arr]
        )  # only used during contains() checks

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
            match: Specifies the subset of objects that match.
                Attribute is a string or Callable. Must be one of the attributes specified in the constructor.
                Value is any hashable type, or it can be a list of values.

                There is an implicit "and" between elements.
                match={'a': 1, 'b': 2} matches all objects with 'a'==1 and 'b'==2.

                When the value is a list, all objects containing any value in the list will match.
                {'a': [1, 2, 3]} matches any object with an 'a' of 1, 2, or 3. Read it as ('a' in [1, 2, 3]).

                If an attribute value is None, objects that are missing the attribute will be matched, as well as
                any objects that have the attribute equal to None.

                match=None means all objects will be matched.

            exclude: Specifies the subset of objects that do not match.

                exclude={'a': 1, 'b': 2} ensures that no objects with 'a'==1 will be in the output, and no
                objects with 'b'==2 will be in the output. Read it as ('a' != 1 and 'b' != 2).

                exclude={'a': [1, 2, 3]} ensures that no objects with 'a' equal to 1, 2, or 3 will be in the output.
                Read it as ('a' not in [1, 2, 3]).

        Returns:
            Numpy array of objects matching the constraints.
        """

        validate_query(self.indices, match, exclude)

        # perform 'match' query
        if match:
            hit_arrays = []
            for attr, value in match.items():
                hit_array = self._match_any_of(attr, value)
                if len(hit_array) == 0:
                    # this attr had no matches, therefore the intersection will be empty. We can stop here.
                    return make_empty_array("O")
                hit_arrays.append(hit_array)

            # intersect all the hit_arrays, starting with the smallest
            for i, hit_array in enumerate(sorted(hit_arrays, key=len)):
                if i == 0:
                    hits = hit_array
                else:
                    hits = snp.intersect(hits, hit_array)
        else:
            hits = np.arange(len(self.obj_arr), dtype=self.dtype)

        # perform 'exclude' query
        if exclude:
            exc_arrays = []
            for attr, value in exclude.items():
                exc_arrays.append(self._match_any_of(attr, value))

            # subtract each of the exc_arrays, starting with the largest
            for exc_array in sorted(exc_arrays, key=len, reverse=True):
                hits = snp_difference(hits, exc_array)
                if len(hits) == 0:
                    break

        return self.obj_arr[hits]

    def get_values(self, attr: Union[str, Callable]) -> Set:
        """Get the unique values we have for the given attribute. Useful for deciding what to find() on.

        Args:
            attr: The attribute to get values for.

        Returns:
            Set of all unique values for this attribute.
        """
        return self.indices[attr].get_values()

    def _match_any_of(
        self, attr: Union[str, Callable], value: Union[Hashable, List[Hashable]]
    ) -> np.ndarray:
        """Get matches for a single attr during a find(). If multiple values specified, handle union logic.

        Args:
            attr: The attribute being queried.
            value: The value of the attr to match, or if list, multiple values to match.

        Returns:
            Sorted array of object IDs.
        """
        if isinstance(value, list):
            matches = [self.indices[attr].get(v) for v in set(value)]
            return np.sort(np.concatenate(matches))
        else:
            if value is ANY:
                return self.indices[attr].get_all()
            return self.indices[attr].get(value)

    def __contains__(self, obj):
        obj_id = id(obj)
        idx = bisect_left(self.sorted_obj_ids, obj_id)
        if idx < 0 or idx >= len(self.sorted_obj_ids):
            return False
        return self.sorted_obj_ids[idx] == obj_id

    def __iter__(self):
        return iter(self.obj_arr)

    def __len__(self):
        return len(self.obj_arr)
