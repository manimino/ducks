from typing import Optional, List, Any, Dict, Set, Callable, Union, Iterable
from cykhash import Int64Set

from operator import itemgetter
from hashindex.exceptions import MissingObjectError, MissingIndexError
from hashindex.utils import get_field
from hashindex.mutable_field import MutableFieldIndex


class HashIndex:
    def __init__(self,
                 objs: Optional[Iterable[Any]] = None,
                 on: Iterable[Union[str, Callable]] = None
                 ):

        self.obj_map = {id(obj): obj for obj in objs}

        # Make an index for each field.
        # Each index is a dict of {field_value: Int64Set(pointers)}.
        self.indices = {}
        for field in on:
            self.indices[field] = MutableFieldIndex(field, self.obj_map)

    def find(
        self,
        match: Optional[Dict[Optional[Union[str, Callable]], Any]] = None,
        exclude: Optional[Dict[Optional[Union[str, Callable]], Any]] = None,
    ) -> List:
        hits = self.find_ids(match, exclude)
        # itemgetter is about 10% faster than doing a comprehension like [self.objs[ptr] for ptr in hits]
        if len(hits) == 0:
            return []
        elif len(hits) == 1:
            return [itemgetter(*hits)(self.obj_map)]  # itemgetter returns a single item here, not in a collection
        else:
            return list(itemgetter(*hits)(self.obj_map))  # itemgetter returns a tuple of items here, so make it a list

    def find_ids(
        self,
        match: Optional[Dict[Optional[Union[str, Callable]], Any]] = None,
        exclude: Optional[Dict[Optional[Union[str, Callable]], Any]] = None,
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
                    # intersecting from the smaller set is faster in cykhash sets
                    if len(hits) < len(field_hits):
                        hits = hits.intersection(field_hits)
                    else:
                        hits = field_hits.intersection(hits)
        else:
            # 'match' is unspecified, so match all objects
            hits = Int64Set(self.obj_map.keys())

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
        self.obj_map[ptr] = obj
        for field in self.indices:
            val = get_field(obj, field)  # TODO add this to the others too, let's have a party
            self._add_to_field_index(ptr, field, val)

    def remove(self, obj):
        ptr = id(obj)
        if ptr not in self.obj_map:
            raise MissingObjectError

        for field in self.indices:
            val = obj.__dict__.get(field, None)
            self._remove_from_field_index(ptr, field, val)
        del self.obj_map[ptr]

    def update(self, obj, new_values: dict):
        ptr = id(obj)
        if ptr not in self.obj_map:
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
                # intersecting based on the larger set is faster in cykhash
                if len(matches) > len(v_matches):
                    matches = matches.union(v_matches)
                else:
                    matches = v_matches.union(matches)
            return matches
        else:
            return self.indices[field].get(value, Int64Set())

    def __contains__(self, obj):
        return self.obj_map.get(id(obj), None) is not None

    def __iter__(self, obj):
        return iter(self.obj_map.values())
