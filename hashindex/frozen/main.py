import numpy as np

from collections.abc import Hashable
from typing import Optional, Any, Dict, Union, Callable, Iterable, List

from hashindex.frozen.frozen_field import FrozenFieldIndex
from hashindex.frozen.array_pair import ArrayPair, make_empty_array_pair, make_array_pair
from hashindex.utils import validate_query


class FrozenHashIndex:
    """A much faster HashIndex that lacks the ability to add or remove objects."""

    def __init__(self, objs: Iterable[Any], on: Iterable[Union[str, Callable]]):
        """Create a FrozenHashIndex containing the objs, queryable by the 'on' attributes.

        Args:
            objs (Any iterable containing any types): The objects that FrozenHashIndex will contain.
                Must contain at least one object. Objects do not need to be hashable, any object works.

            on (Iterable of attributes): The attributes that FrozenHashIndex will build indices on.
                Must contain at least one.

        Objects in obj do not need to have all of the attributes in 'on'. Objects will be considered to have a
        None value for missing attributes.
        """
        if not objs:
            raise ValueError(
                "Cannot build an empty FrozenHashIndex; at least 1 object is required."
            )
        self.on = on
        self.indices = {}
        self.all = make_array_pair(np.array(objs, dtype='O'))
        for field in on:
            self.indices[field] = FrozenFieldIndex(field, objs)

    def find(
        self,
        match: Optional[Dict[Union[str, Callable], Union[Hashable, List[Hashable]]]] = None,
        exclude: Optional[Dict[Union[str, Callable], Union[Hashable, List[Hashable]]]] = None,
    ) -> np.ndarray:
        """Find objects in the FrozenHashIndex that satisfy the match and exclude constraints.

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
                if hits is None:  # first field
                    hits = field_hits
                if field_hits:
                    # intersect this field's hits with our hits so far
                    hits.apply_intersection(field_hits)
                else:
                    # this field had no matches, therefore the intersection will be empty. We can stop here.
                    return make_empty_array_pair().obj_arr
        else:
            # 'match' is unspecified, so match all objects
            hits = self.all

        # perform 'exclude' query
        if exclude:
            for field, value in exclude.items():
                field_hits = self._match_any_of(field, value)
                print(hits.obj_arr, 'minus', field_hits.obj_arr)
                hits.apply_difference(field_hits)
                if len(hits) == 0:
                    break
        print(hits.obj_arr)

        return hits.obj_arr

    def _match_any_of(self, field: Union[str, Callable], value: Union[Hashable, List[Hashable]]) -> ArrayPair:
        """Get matches for a single field during a find(). If multiple values specified, handle union logic.

        Args:
            field: The attribute being queried.
            value: The value of the field to match, or if list, multiple values to match.

        Returns:
            ArrayPair of matched objects and their IDs, both sorted by ID.
        """
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
        """Return all objects in the FrozenHashIndex. Used by find() when match=None."""
        return self.all()

    def __contains__(self, obj):
        return obj in self.all

    def __iter__(self):
        return iter(self.all.obj_arr)

    def __len__(self):
        for idx in self.indices.values():
            return len(idx)
