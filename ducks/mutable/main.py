import pickle
from operator import itemgetter
from typing import Optional, List, Any, Dict, Callable, Union, Iterable, Set

from cykhash import Int64Set

from ducks.utils import (
    cyk_intersect,
    cyk_union,
    split_query,
    standardize_expr,
    validate_query,
)
from ducks.mutable.mutable_attr import MutableAttrIndex


class Dex:

    def __init__(
        self,
        objs: Optional[Iterable[Any]] = None,
        on: Iterable[Union[str, Callable]] = None,
    ):
        """
        Create a Dex containing the ``objs``, queryable by the ``on`` attributes.

        Args:
            objs: The objects that Dex will contain initially. Optional.

            on: The attributes that will be used for finding objects.
                Must contain at least one.

        It's OK if the objects in ``objs`` are missing some or all of the attributes in ``on``.

        For the objects that do contain the attributes in ``on``, those attribute values must be hashable and sortable.
        Most Python objects are hashable. Implement the function ``__lt__(self, other)`` to make a class sortable.
        An attribute value of ``None`` is acceptable as well, even though None is not sortable.
        """
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

    def _find(
        self,
        match: Dict[Union[str, Callable], Dict[str, Any]],
        exclude: Dict[Union[str, Callable], Dict[str, Any]],
    ) -> List:
        """Find objects in the Dex that satisfy the match and exclude constraints.

        Args:
            match: Dict of ``{attribute: expression}`` defining the subset of objects that match.
                If ``None``, all objects will match.

                Each attribute is a string or Callable. Must be one of the attributes specified in the constructor.

                The expression can be any of the following:
                 - A dict of ``{operator: value}``, such as ``{'==': 1}`` ``{'>': 5}``, or ``{'in': [1, 2, 3]}``.
                 - A single value, which is a shorthand for `{'==': value}`.
                 - A list of values, which is a shorthand for ``{'in': [list_of_values]}``.

                 The special value ``ducks.ANY`` will match all objects having the attribute.

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
        """Get the unique values we have for the given attribute.

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

    def __getitem__(self, query: Dict) -> List[Any]:
        """Find objects in the Dex that satisfy the constraints.

                Args:
                    query: Dict of ``{attribute: expression}`` defining the subset of objects that match.
                        If ``{}``, all objects will match.

                        Each attribute is a string or Callable. Must be one of the attributes specified in the constructor.

                        The expression can be any of the following:
                         - A dict of ``{operator: value}``, such as ``{'==': 1}`` ``{'>': 5}``, or ``{'in': [1, 2, 3]}``.
                         - A single value, which is a shorthand for `{'==': value}`.
                         - A list of values, which is a shorthand for ``{'in': [list_of_values]}``.

                         The expression ``{'==': ducks.ANY}`` will match all objects having the attribute.
                         The expression ``{'!=': ducks.ANY}`` will match all objects without the attribute.

                         Valid operators are '==', '!=', 'in', 'not in', '<', '<=', '>', '>='.
                         The aliases 'eq', 'ne', 'lt', 'le', 'lte', 'gt', 'ge', and 'gte' work too.
                         To match a None value, use ``{'==': None}``. There is no separate operator for None values.

                Returns:
                    List of objects matching the constraints. List will be unordered.
        """
        if not isinstance(query, dict):
            raise TypeError(f"Got {type(query)}; expected a dict.")
        std_query = dict()
        for attr, expr in query.items():
            std_query[attr] = standardize_expr(expr)
        match_query, exclude_query = split_query(std_query)
        return self._find(match_query, exclude_query)


def save(box: Dex, filepath: str):
    """Saves this object to a pickle file."""
    # We can't pickle this easily, because:
    # - Int64Sets cannot be pickled, so the MutableAttrIndex is hard to save.
    # - Object IDs are specific to the process that created them, so the object map will be invalid if saved.
    # Therefore, this just pickles the objects and the list of what to build indexes on.
    # The Dex container will be built anew with __init__ on load.
    # A bit slow, but it's simple, guaranteed to work, and is very robust against changes in the container code.
    saved = {"objs": list(box.obj_map.values()), "on": list(box._indexes.keys())}
    with open(filepath, "wb") as fh:
        pickle.dump(saved, fh)


def load(saved: Dict) -> Dex:
    """Creates a Dex from the pickle file."""
    return Dex(saved["objs"], saved["on"])
