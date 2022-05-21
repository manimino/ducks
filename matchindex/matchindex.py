from typing import Iterable, Optional, List, Any, Dict


class MatchIndex:
    def __init__(self, fields: Iterable[str]):
        # the objects themselves are stored in a dict of {pointer: obj}
        self.objs = dict()

        # Make an index for each field.
        # Each index is a dict of {field_value: set(pointers)}.
        self.indices = {}
        for field in fields:
            self.indices[field] = dict()

    def add(self, obj):
        """Add object to collection, update indices."""
        self.objs[id(obj)] = obj

        # update indices
        for field in self.indices:
            val = obj.__dict__[field]
            idx = self.indices[field]
            if val not in idx:
                idx[val] = set()
            idx[val].add(id(obj))

    def values_of(self, field) -> Iterable:
        """Get available values for a given field."""
        if field not in self.indices:
            raise MissingIndexError
        return self.indices[field].keys()

    def _matches_for(self, field: str, value: Any):
        """Get matches during a find(). Helper function to handle union-on-list logic."""
        if type(value) is list:
            # take the union of all matches
            matches = set()
            for v in value:
                v_matches = self.indices[field].get(v, set())
                matches = set.union(matches, v_matches)
            return matches
        else:
            return self.indices[field].get(value, set())

    def find(self, match: Optional[Dict[str, Any]] = None, exclude: Optional[Dict[str, Any]] = None) -> List:
        """
        Perform lookup based on given values.

        If "having" is None / empty, it matches all objects.
        There is an implicit "AND" joining all constraints.
        """
        # check that we have an index for all desired lookups
        required_indices = set()
        if match:
            required_indices.update(match.keys())
        if exclude:
            required_indices.update(exclude.keys())
        missing_indices = required_indices.difference(self.indices)
        if missing_indices:
            raise MissingIndexError

        hits = None
        if match:
            # result is the intersection of all query items
            for field, value in match.items():
                field_hits = self._matches_for(field, value)
                if hits is None:
                    hits = field_hits
                if not field_hits:
                    break
                else:
                    hits = set.intersection(hits, field_hits)
        else:
            hits = set(self.objs.keys())

        if exclude:
            for field, value in exclude.items():
                field_hits = self._matches_for(field, value)
                hits = set.difference(hits, field_hits)

        return [self.objs[ptr] for ptr in hits]

    def remove(self, obj):
        """Delete object and update indices."""
        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError

        for field in self.indices:
            val = obj.__dict__[field]
            idx = self.indices[field]
            idx[val].remove(ptr)
            if not idx[val]:
                del idx[val]
        del self.objs[ptr]

    def update(self, obj, changes: dict):
        """Update fields of an existing object"""
        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError
        for field, new_value in changes.items():
            # update obj
            old_value = obj.__dict__[field]
            obj.__dict__[field] = new_value
            # update index
            if field in self.indices:
                idx = self.indices[field]
                idx[old_value].remove(ptr)
                if not idx[old_value]:
                    del idx[old_value]

                if new_value not in idx:
                    idx[new_value] = set()
                idx[new_value].add(ptr)


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
