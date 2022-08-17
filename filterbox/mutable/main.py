from operator import itemgetter
from typing import Optional, List, Any, Dict, Callable, Union, Iterable, Set

from cykhash import Int64Set

from filterbox.utils import cyk_intersect, cyk_union, standardize_expr, validate_query
from filterbox.mutable.mutable_attr import MutableAttrIndex


class FilterBox:
    """
    Create a FilterBox containing the ``objs``, queryable by the ``on`` attributes.

    Args:
        objs: The objects that FilterBox will contain initially. Optional.

        on: The attributes that will be used for finding objects.
            Must contain at least one.

    It's OK if the objects in ``objs`` are missing some or all of the attributes in ``on``. They will still be
    stored, and can found with ``find()``.

    For the objects that do contain the attributes on ``on``, those attribute values must be hashable and sortable.
    Most Python objects are hashable. Implement the function ``__lt__(self, other)`` to make a class sortable.
    An attribute value of ``None`` is acceptable as well, even though None is not sortable.
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
        self._indexes = {}
        for attr in on:
            self._indexes[attr] = MutableAttrIndex(attr, objs)

    def find(
        self,
        match: Optional[Dict[Union[str, Callable], Any]] = None,
        exclude: Optional[Dict[Union[str, Callable], Any]] = None,
    ) -> List:
        """Find objects in the FilterBox that satisfy the match and exclude constraints.

        Args:
            match: Dict of ``{attribute: expression}`` defining the subset of objects that match.
                If ``None``, all objects will match.

                Each attribute is a string or Callable. Must be one of the attributes specified in the constructor.

                The expression can be any of the following:
                 - A dict of ``{operator: value}``, such as ``{'==': 1}`` ``{'>': 5}``, or ``{'in': [1, 2, 3]}``.
                 - A single value, which is a shorthand for `{'==': value}`.
                 - A list of values, which is a shorthand for ``{'in': [list_of_values]}``.

                 The special value ``filterbox.ANY`` will match all objects having the attribute.

                 Valid operators are '==' 'in', '<', '<=', '>', '>='.
                 The aliases 'eq' 'lt', 'le', 'lte', 'gt', 'ge', and 'gte' work too.
                 To match a None value, use ``{'==': None}``. There is no separate operator for None values.

            exclude: Dict of ``{attribute: expression}`` defining the subset of objects that do not match.
                If ``None``, no objects will be excluded.

                Each attribute is a string or Callable. Must be one of the attributes specified in the constructor.
                Valid expressions are the same as in ``match``.

        Returns:
            List of objects matching the constraints. List will be unordered.
        """
        # validate input and convert expressions to dict
        validate_query(self._indexes, match, exclude)
        for arg in [match, exclude]:
            if arg:
                for key in arg:
                    arg[key] = standardize_expr(arg[key])

        obj_ids = self._find_ids(match, exclude)
        return self._obj_ids_to_objs(obj_ids)

    def add(self, obj: Any):
        """Add the object, evaluating any attributes and storing the results.
        If the object is already present, it will not be updated."""
        ptr = id(obj)
        if ptr in self.obj_map:
            return
        self.obj_map[ptr] = obj
        for attr in self._indexes:
            self._indexes[attr].add(ptr, obj)

    def remove(self, obj: Any):
        """Remove the object. Raises KeyError if not present."""
        ptr = id(obj)
        if ptr not in self.obj_map:
            raise KeyError

        for attr in self._indexes:
            self._indexes[attr].remove(ptr, obj)
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
        return self._indexes[attr].get_values()

    def _find_ids(
        self,
        match: Optional[Dict[Union[str, Callable], Dict]] = None,
        exclude: Optional[Dict[Union[str, Callable], Dict]] = None,
    ) -> Int64Set:
        """Perform lookup based on given constraints. Return a set of object IDs."""
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

    def _match_attr_expr(
        self, attr: Union[str, Callable], expr: Dict[str, Any]
    ) -> Int64Set:
        """Look at an attr, handle its expr appropriately"""
        matches = None
        # handle 'in' and '=='
        eq_expr = {op: val for op, val in expr.items() if op in ["==", "in"]}
        for op, val in eq_expr.items():
            if op == "==":
                op_matches = self._indexes[attr].get_obj_ids(val)
            elif op == "in":
                op_matches = self._match_any_value_in(attr, expr["in"])
            matches = (
                op_matches if matches is None else cyk_intersect(op_matches, matches)
            )

        # handle range query
        range_expr = {
            op: val for op, val in expr.items() if op in ["<", ">", "<=", ">="]
        }
        if range_expr:
            range_matches = self._indexes[attr].get_ids_by_range(range_expr)
            matches = (
                range_matches
                if matches is None
                else cyk_intersect(range_matches, matches)
            )
        return matches

    def _match_any_value_in(
        self, attr: Union[str, Callable], values: Iterable[Any]
    ) -> Int64Set:
        """Handle 'in' queries. Return the union of object ID matches for the values."""
        matches = Int64Set()
        for v in values:
            v_matches = self._indexes[attr].get_obj_ids(v)
            matches = cyk_union(matches, v_matches)
        return Int64Set(matches)

    def _obj_ids_to_objs(self, obj_ids: Int64Set) -> List[Any]:
        """Look up each obj_id in self.obj_map, and return the list of objs."""
        # Using itemgetter is about 10% faster than doing a comprehension like [self.objs[ptr] for ptr in hits]
        if len(obj_ids) == 0:
            return []
        elif len(obj_ids) == 1:
            return [
                itemgetter(*obj_ids)(self.obj_map)
            ]  # itemgetter returns a single item here, not in a collection
        else:
            return list(
                itemgetter(*obj_ids)(self.obj_map)
            )  # itemgetter returns a tuple of items here, so make it a list

    def __contains__(self, obj: Any):
        return id(obj) in self.obj_map

    def __iter__(self):
        return iter(self.obj_map.values())

    def __len__(self):
        return len(self.obj_map)
