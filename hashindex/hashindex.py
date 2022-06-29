from typing import Iterable, Optional, List, Any, Dict, Set

from cykhash import Int64Set
import numpy as np
import sortednp
from hashindex.exceptions import WriteLockedError


class HashIndex:
    def __init__(self, fields: Iterable[str]):
        # Make an index for each field.
        # Each index is a dict of {field_value: set(pointers)}.
        self.indices = {}
        for field in fields:
            self.indices[field] = dict()

        # lookup table for objs
        self.objs = dict()

        self.frozen = False  # See freeze() method

    def find(self, match: Optional[Dict[str, Any]] = None, exclude: Optional[Dict[str, Any]] = None) -> List:
        """
        Find objects that fit the query.

        Example: find(match={'color': ['red', 'green'], size='big'}, exclude={'shape': 'round') will return objects
        with color ('red' OR 'green') AND that are size 'big' AND NOT round.

        If the "match" term is None, all objects in the index will be matched.
        """
        hits = self.find_ids(match, exclude)
        if isinstance(self.objs, dict):
            return [self.objs[ptr] for ptr in hits]
        else:
            return self.objs.get(hits)

    def add(self, obj):
        """Add object to collection, update indices."""
        if self.frozen:
            raise WriteLockedError('Cannot add item - index is frozen.')

        ptr = id(obj)
        self.objs[ptr] = obj

        for field in self.indices:
            val = obj.__dict__.get(field, None)
            self._add_to_field_index(ptr, field, val)

    def remove(self, obj):
        """Delete object and update indices."""
        if self.frozen:
            raise WriteLockedError('Cannot remove item - index is frozen.')

        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError

        for field in self.indices:
            val = obj.__dict__.get(field, None)
            self._remove_from_field_index(ptr, field, val)
        del self.objs[ptr]

    def update(self, obj, new_values: dict):
        """
        Update the HashIndex for a changed object. Also applies the update to the object.

        new_values contains {field: new_value} for each changed field.
        """
        if self.writes_locked:
            raise WriteLockedError('Cannot update item - index is frozen.')

        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError
        for field, new_value in new_values.items():
            # update obj
            old_value = obj.__dict__.get(field, None)
            obj.__dict__[field] = new_value
            # update index
            if field in self.indices:
                self._remove_from_field_index(ptr, field, old_value)
                self._add_to_field_index(ptr, field, new_value)

    def find_ids(self, match: Optional[Dict[str, Any]] = None, exclude: Optional[Dict[str, Any]] = None) -> Set:
        """
        Perform lookup based on given values. Return a set of object IDs matching constraints.

        If "having" is None / empty, it matches all objects.
        There is an implicit "AND" joining all constraints.
        """

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
        hits = None
        if match:
            # find intersection of each field
            for field, value in match.items():
                field_hits = self._match_any_of(field, value)
                if hits is None:
                    hits = field_hits
                if not field_hits:
                    # this was empty, so intersection will be empty
                    hits = Int64Set()
                    break
                else:
                    hits = hits.intersection(field_hits)
        else:
            # 'match' is unspecified, so match all objects
            hits = set(self.objs.keys())

        # perform 'exclude' query
        if exclude:
            for field, value in exclude.items():
                field_hits = self._match_any_of(field, value)
                hits = set.difference(hits, field_hits)

        return hits

    def freeze(self):
        """
        Prevent future changes to the index. Makes find() faster. Reduces RAM usage.

        Any attempts to add / update / remove from a frozen index will throw exceptions.
        Call this method before using HashIndex in a multithreaded environment.

        There is no unlock(), just make a new index if you want that. To make a new index, you can do:
        new_index = HashIndex(this_index.fields)
        for obj in this_index:
            new_index.add(obj)
        """
        self.frozen = True
        # Convert each set of object ids to a sorted numpy array
        # intersect operations can use the super fast compare-sorted logic
        # unions, ehh, isn't there a np.union thing? does it preserve sort order?
        # https://numpy.org/doc/stable/reference/generated/numpy.union1d.html  Hell yeah it does
        # https://numpy.org/doc/stable/reference/generated/numpy.intersect1d.html  also does this
        # Convert self.objs into a pair of sorted numpy arrays for faster lookup there too
        # this should be awe; initially dict(), changes to two parallel numpy arrays on freezesome

    def values_of(self, field) -> Iterable:
        """Get available values for a given field."""
        if field not in self.indices:
            raise MissingIndexError
        return self.indices[field].keys()

    def _add_to_field_index(self, ptr: int, field: str, val: Any):
        """
        Add an object's pointer to the appropriate field index slot.

        If elements > THRESH_HIGH, change underlying data structure from tuple to set.
        """
        idx = self.indices[field]
        if val not in idx:
            # make new set of obj ids
            idx[val] = Int64Set()
        idx[val].add(ptr)

    def _remove_from_field_index(self, ptr: int, field: str, val: Any):
        """
        Remove an object's pointer from a field index slot.

        If fewer than THRESH_LOW elements remain, change the underlying data structure from set to tuple.
        If 0 elements remain, remove the value from the field index.
        """
        idx = self.indices[field]
        if len(idx[val]) == 1:
            # no more pointers for this value, remove value
            del idx[val]
        else:
            idx[val].remove(ptr)

    def _match_any_of(self, field: str, value: Any):
        """Get matches during a find(). If multiple values specified, handle union logic."""
        if type(value) is list:
            # take the union of all matches
            matches = set()
            for v in value:
                v_matches = self.indices[field].get(v, set())
                matches = set.union(matches, v_matches)  # v_matches can be a tuple here, it's OK
            return matches
        else:
            matches = self.indices[field].get(value, set())
            if isinstance(matches, tuple):
                return set(matches)
            return matches

    def __contains__(self, obj):
        return self.objs.get(id(obj), None) is not None

    def __iter__(self):
        pass


class HashIndexIterator:



def get_attributes(cls) -> List[str]:
    """Helper function to grab the attributes of a class"""
    return list(cls.__annotations__.keys())


class MissingIndexError(Exception):
    """Raised when querying a field we don't have an index for"""
    pass


class MissingValueError(Exception):
    """Raised when adding an object that is missing a field we need to index"""
    pass


class MissingObjectError(Exception):
    """Raised when removing or updating an object we don't have."""
    pass
