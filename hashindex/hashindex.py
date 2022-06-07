from typing import Iterable, Optional, List, Any, Dict, Set

# These size thresholds determine whether a tuple or set is used to store the matching objects for a field value.
# When there are few objects, a tuple's RAM-efficiency makes it the better container.
# At a high number of objects, a set becomes necessary for lookup speed reasons.
# There are two thresholds to give hysteresis; we don't want to convert between the two repeatedly for small changes.
THRESH_LOW = 50
THRESH_HIGH = 100


class HashIndex:
    def __init__(self, fields: Iterable[str]):
        # the objects themselves are stored in a dict of {pointer: obj}
        self.objs = dict()

        # Make an index for each field.
        # Each index is a dict of {field_value: set(pointers)}.
        self.indices = {}
        for field in fields:
            self.indices[field] = dict()

    def find(self, match: Optional[Dict[str, Any]] = None, exclude: Optional[Dict[str, Any]] = None) -> List:
        """
        Find objects that fit the query.

        Example: find(match={'color': ['red', 'green'], size='big'}, exclude={'shape': 'round') will return objects
        with color ('red' OR 'green') AND that are size 'big' AND NOT round.

        If the "match" term is None, all objects in the index will be matched.
        """
        hits = self.find_ids(match, exclude)
        return [self.objs[ptr] for ptr in hits]

    def add(self, obj):
        """Add object to collection, update indices."""
        ptr = id(obj)
        self.objs[ptr] = obj

        for field in self.indices:
            val = obj.__dict__[field]
            self._add_to_field_index(ptr, field, val)

    def remove(self, obj):
        """Delete object and update indices."""
        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError

        for field in self.indices:
            val = obj.__dict__[field]
            self._remove_from_field_index(ptr, field, val)
        del self.objs[ptr]

    def update(self, obj, new_values: dict):
        """
        Update the HashIndex for a changed object. Also applies the update to the object.

        new_values contains {field: new_value} for each changed field.
        """
        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError
        for field, new_value in new_values.items():
            # update obj
            old_value = obj.__dict__[field]
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
                    hits = set()
                    break
                else:
                    hits = set.intersection(hits, field_hits)
        else:
            # 'match' is unspecified, so match all objects
            hits = set(self.objs.keys())

        # perform 'exclude' query
        if exclude:
            for field, value in exclude.items():
                field_hits = self._match_any_of(field, value)
                hits = set.difference(hits, field_hits)

        return hits

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
            # make new tuple of obj ids
            idx[val] = (ptr,)
        elif isinstance(idx[val], tuple):
            if len(idx[val]) <= THRESH_HIGH:
                # "append" by copying to a new tuple (very fast for small n)
                idx[val] = idx[val] + (ptr,)
            else:
                # we have too many items for a tuple. Change to a set.
                idx[val] = set(idx[val])
                idx[val].add(ptr)
        else:
            # add to set
            idx[val].add(ptr)

    def _remove_from_field_index(self, ptr: int, field: str, val: Any):
        """
        Remove an object's pointer from a field index slot.

        If fewer than THRESH_LOW elements remain, change the underlying data structure from set to tuple.
        If 0 elements remain, remove the value from the field index.
        """
        idx = self.indices[field]
        if isinstance(idx[val], tuple):
            if len(idx[val]) == 1:
                # no more pointers for this value, remove value
                del idx[val]
            else:
                idx[val] = tuple(p for p in idx[val] if p!=ptr)
        else:
            idx[val].remove(ptr)
            if len(idx[val]) < THRESH_LOW:
                # change to using a tuple to hold these values
                idx[val] = tuple(idx[val])

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
