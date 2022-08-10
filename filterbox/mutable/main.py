from operator import itemgetter
from typing import Optional, List, Any, Dict, Callable, Union, Iterable, Set

from cykhash import Int64Set

from filterbox import ANY
from filterbox.utils import cyk_intersect, cyk_union, validate_query, filter_vals
from filterbox.mutable.mutable_attr import MutableAttrIndex


class FilterBox:
    """
    Create a FilterBox containing the ``objs``, queryable by the ``on`` attributes.

    Args:
        objs: The objects that FilterBox will contain initially.
            Objects do not need to be hashable, any object works.

        on: The attributes that will be used for finding objects.
            Must contain at least one.

    It's OK if the objects in ``objs`` are missing some or all of the attributes in ``on``. They will still be
    stored, and can found with ``find()``.

    For the objects that do contain the ``on`` attributes, those attribute values must be hashable.
    """

    def __init__(
        self,
        objs: Optional[Iterable[Any]] = None,
        on: Iterable[Union[str, Callable]] = None,
    ):
        if not on:
            raise ValueError("Need at least one attribute.")
        if isinstance(on, str):
            on = [on]

        if objs:
            self.obj_map = {id(obj): obj for obj in objs}
        else:
            self.obj_map = dict()

        # Build an index for each attribute
        self._indices = {}
        for attr in on:
            self._indices[attr] = MutableAttrIndex(attr, self.obj_map, objs)

    def find(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> List:
        """Find objects in the FilterBox that satisfy the match and exclude constraints.

        Args:
            match: Dict of ``{attribute: value}`` defining the subset of objects that match.
                If ``None``, all objects will match.

                Each attribute is a string or Callable. Must be one of the attributes specified in the constructor.

                Value can be any of the following:
                 - A single hashable value, which will match all objects with that value for the attribute.
                 - A dict specifying operators and values, such as ``{'>' 3}`` or ``{'in': [1, 2, 3]}``.
                 - ``filterbox.ANY``, which matches all objects having the attribute.

                 Valid operators are 'in', '<', '<=', '>', '>=', 'lt', 'le', 'lte', 'gt', 'ge', and 'gte'.

            exclude: Dict of ``{attribute: value}`` defining the subset of objects that do not match.
                If ``None``, no objects will be excluded.

                Each attribute is a string or Callable. Must be one of the attributes specified in the constructor.

                Value can be any of the following:
                 - A single hashable value, which will exclude all objects with that value for the attribute.
                 - A dict specifying operators and values to exclude, such as ``{'>' 3}`` or ``{'in': [1, 2, 3]}``
                 - ``filterbox.ANY``, which excludes all objects having the attribute.

        Returns:
            List of objects matching the constraints.
        """
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
        """Perform lookup based on given constraints. Return a set of object IDs."""
        validate_query(self._indices, match, exclude)

        # perform 'match' query
        if match:
            # find intersection of each attr
            hit_sets = []
            for attr, expr in match.items():
                hit_set = self._match_attr_expr(attr, expr)
                if len(hit_set) == 0:
                    # this attr had no matches, therefore the intersection will be empty. We can stop here.
                    return Int64Set()
                hit_sets.append(hit_set)

            for i, hit_set in enumerate(sorted(hit_sets, key=len)):
                # intersect this attr's hits with our hits so far
                if i == 0:
                    hits = hit_set
                else:
                    hits = cyk_intersect(hits, hit_set)
        else:
            # 'match' is unspecified, so match all objects
            hits = Int64Set(self.obj_map.keys())

        # perform 'exclude' query
        if exclude:
            exc_sets = []
            for attr, expr in exclude.items():
                exc_sets.append(self._match_attr_expr(attr, expr))

            for exc_set in sorted(exc_sets, key=len, reverse=True):
                hits = Int64Set.difference(hits, exc_set)
                if len(hits) == 0:
                    break

        return hits

    def add(self, obj: Any):
        """Add the object, evaluating any attributes and storing the results.
        If the object is already present, it will not be updated."""
        ptr = id(obj)
        if ptr in self.obj_map:
            return
        self.obj_map[ptr] = obj
        for attr in self._indices:
            self._indices[attr].add(ptr, obj)

    def remove(self, obj: Any):
        """Remove the object. Raises KeyError if not present."""
        ptr = id(obj)
        if ptr not in self.obj_map:
            raise KeyError

        for attr in self._indices:
            self._indices[attr].remove(ptr, obj)
        del self.obj_map[ptr]

    def update(self, obj: Any):
        """Remove and re-add the object, updating all stored attributes. Raises KeyError if object not present."""
        self.remove(obj)
        self.add(obj)

    def get_values(self, attr: Union[str, Callable]) -> Set:
        """Get the unique values we have for the given attribute. Useful for deciding what to ``find()`` on.

        Args:
            attr: The attribute to get values for.

        Returns:
            Set of all unique values for this attribute.
        """
        return self._indices[attr].get_values()

    def _match_attr_expr(self, attr, expr) -> Int64Set:
        """Look at an attr, handle its expr appropriately"""
        if isinstance(expr, dict):
            matches = None
            if "in" in expr:
                # always do 'in' first -- it doesn't require get_values() which can be slow.
                matches = self._match_any_value_in(attr, expr["in"])
                del expr["in"]
            if expr:
                # handle <, >, etc
                attr_vals = self._indices[attr].get_values()
                valid_values = filter_vals(attr_vals, expr)
                expr_matches = self._match_any_value_in(attr, valid_values)
                if matches is None:
                    matches = expr_matches
                else:
                    matches = matches.intersection(expr_matches)
            return matches
        elif expr is ANY:
            return self._indices[attr].get_all_ids()
        elif isinstance(expr, set):
            raise ValueError(
                f"Expression {expr} is a set. Did you mean to make a dict?"
            )
        else:
            # match this specific value
            return self._indices[attr].get_obj_ids(expr)

    def _match_any_value_in(
        self, attr: Union[str, Callable], values: Iterable[Any]
    ) -> Int64Set:
        """Get the union of object ID matches for the values."""
        # Note: this could also be done with list operations, but union() is slightly faster in most cases.
        matches = Int64Set()
        for v in values:
            v_matches = self._indices[attr].get_obj_ids(v)
            matches = cyk_union(matches, v_matches)
        return Int64Set(matches)

    def __contains__(self, obj: Any):
        return id(obj) in self.obj_map

    def __iter__(self):
        return iter(self.obj_map.values())

    def __len__(self):
        return len(self.obj_map)
