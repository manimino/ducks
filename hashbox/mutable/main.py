from operator import itemgetter
from typing import Optional, List, Any, Dict, Callable, Union, Iterable

from cykhash import Int64Set

from hashbox import ANY
from hashbox.utils import validate_query
from hashbox.mutable.mutable_attr import MutableAttrIndex


class HashBox:
    def __init__(
        self,
        objs: Optional[Iterable[Any]] = None,
        on: Iterable[Union[str, Callable]] = None,
    ):
        if not on:
            raise ValueError("Need at least one attribute.")
        if objs:
            self.obj_map = {id(obj): obj for obj in objs}
        else:
            self.obj_map = dict()

        # Build an index for each attribute
        self.indices = {}
        for attr in on:
            self.indices[attr] = MutableAttrIndex(attr, self.obj_map, objs)

    def find(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> List:
        hits = self._find_ids(match, exclude)
        # itemgetter is about 10% faster than doing a comprehension like [self.objs[ptr] for ptr in hits]
        if len(hits) == 0:
            return []
        elif len(hits) == 1:
            return [
                itemgetter(*hits)(self.obj_map)
            ]  # itemgetter returns a single item here, not in a collection
        else:
            return list(
                itemgetter(*hits)(self.obj_map)
            )  # itemgetter returns a tuple of items here, so make it a list

    def _find_ids(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> Int64Set:
        """
        Perform lookup based on given values. Return a set of object IDs matching constraints.

        If "having" is None / empty, it matches all objects.
        There is an implicit "AND" joining all constraints.
        """
        validate_query(self.indices, match, exclude)

        # perform 'match' query
        if match:
            # find intersection of each attr
            hit_sets = []
            for attr, value in match.items():
                # if multiple values for a attr, find each value and union those first
                hit_set = self._match_any_of(attr, value)
                if len(hit_set) == 0:
                    # this attr had no matches, therefore the intersection will be empty. We can stop here.
                    return Int64Set()
                hit_sets.append(hit_set)

            for i, hit_set in enumerate(sorted(hit_sets, key=len)):
                # intersect this attr's hits with our hits so far
                if i == 0:
                    hits = hit_set
                else:
                    # intersecting with the smaller set on the left is faster in cykhash sets
                    if len(hits) < len(hit_set):
                        hits = hits.intersection(hit_set)
                    else:
                        hits = hit_set.intersection(hits)
        else:
            # 'match' is unspecified, so match all objects
            hits = Int64Set(self.obj_map.keys())

        # perform 'exclude' query
        if exclude:
            exc_sets = []
            for attr, value in exclude.items():
                exc_sets.append(self._match_any_of(attr, value))

            for exc_set in sorted(exc_sets, key=len, reverse=True):
                hits = Int64Set.difference(hits, exc_set)
                if len(hits) == 0:
                    break

        return hits

    def add(self, obj):
        """Add a new object, evaluating any attributes and storing the results."""
        ptr = id(obj)
        self.obj_map[ptr] = obj
        for attr in self.indices:
            self.indices[attr].add(ptr, obj)

    def remove(self, obj):
        """Remove an object. Raises KeyError if not present."""
        ptr = id(obj)
        if ptr not in self.obj_map:
            raise KeyError

        for attr in self.indices:
            self.indices[attr].remove(ptr, obj)
        del self.obj_map[ptr]

    def _match_any_of(self, attr: str, value: Any):
        """Get matches for a single attr during a find(). If multiple values specified, handle union logic."""
        if isinstance(value, list):
            # take the union of all matches
            matches = Int64Set()
            for v in value:
                v_matches = self.indices[attr].get_obj_ids(v)
                # union with the larger set on the left is faster in cykhash
                if len(matches) > len(v_matches):
                    matches = matches.union(v_matches)
                else:
                    matches = v_matches.union(matches)
            return matches
        else:
            if value is ANY:
                return self.indices[attr].get_all_ids()
            else:
                return self.indices[attr].get_obj_ids(value)

    def __contains__(self, obj):
        return id(obj) in self.obj_map

    def __iter__(self):
        return iter(self.obj_map.values())

    def __len__(self):
        return len(self.obj_map)
