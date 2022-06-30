from typing import Optional, List, Any, Dict, Set

from cykhash import Int64Set

from hashindex.exceptions import MissingObjectError, MissingIndexError


class MutableIndex:
    def __init__(self, fields):
        # Make an index for each field.
        # Each index is a dict of {field_value: Int64Set(pointers)}.
        self.indices = {}
        for field in fields:
            self.indices[field] = dict()

        # lookup table for objs
        self.objs = dict()

        self.frozen = False  # See freeze() method

    def find(
        self,
        match: Optional[Dict[str, Any]] = None,
        exclude: Optional[Dict[str, Any]] = None,
    ) -> List:
        hits = self.find_ids(match, exclude)
        if isinstance(self.objs, dict):
            return [self.objs[ptr] for ptr in hits]
        else:
            return self.objs.get(hits)

    def find_ids(
        self,
        match: Optional[Dict[str, Any]] = None,
        exclude: Optional[Dict[str, Any]] = None,
    ) -> Set:
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
            hits = Int64Set(self.objs.keys())

        # perform 'exclude' query
        if exclude:
            for field, value in exclude.items():
                field_hits = self._match_any_of(field, value)
                hits = Int64Set.difference(hits, field_hits)
                if len(hits) == 0:
                    break

        return hits

    def add(self, obj):
        ptr = id(obj)
        self.objs[ptr] = obj

        for field in self.indices:
            val = obj.__dict__.get(field, None)
            self._add_to_field_index(ptr, field, val)

    def remove(self, obj):
        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError

        for field in self.indices:
            val = obj.__dict__.get(field, None)
            self._remove_from_field_index(ptr, field, val)
        del self.objs[ptr]

    def update(self, obj, new_values: dict):
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

    def _add_to_field_index(self, ptr: int, field: str, val: Any):
        """Add an object's pointer to the appropriate field index slot."""
        idx = self.indices[field]
        if val not in idx:
            # make new set of obj ids
            idx[val] = Int64Set()
        idx[val].add(ptr)

    def _remove_from_field_index(self, ptr: int, field: str, val: Any):
        """
        Remove an object's pointer from a field index slot.

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
            matches = Int64Set()
            for v in value:
                v_matches = self.indices[field].get(v, Int64Set())
                matches = Int64Set.union(
                    matches, v_matches
                )
            return matches
        else:
            return self.indices[field].get(value, Int64Set())

    def __contains__(self, obj):
        return self.objs.get(id(obj), None) is not None

    def __iter__(self, obj):
        return iter(self.objs.values())
