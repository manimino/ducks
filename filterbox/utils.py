import numpy as np

from typing import List, Union, Callable, Optional, Any, Dict, Tuple, Set

from cykhash import Int64Set

from filterbox.constants import VALID_OPERATORS, OPERATOR_MAP
from filterbox.exceptions import AttributeNotFoundError, MissingAttribute


def get_attribute(obj: Any, attr: Union[Callable, str]) -> Tuple[Any, bool]:
    """Get the object's attribute value. Return (value, success). Unsuccessful if attribute is missing."""
    if callable(attr):
        try:
            val = attr(obj)
        except MissingAttribute:
            return None, False
    elif isinstance(obj, dict):
        try:
            val = obj[attr]
        except KeyError:
            return None, False
    else:
        try:
            val = getattr(obj, attr)
        except AttributeError:
            return None, False
    return val, True


def get_attributes(cls) -> List[str]:
    """Helper function to grab the attributes of a class"""
    return list(cls.__annotations__.keys())


def validate_query(
    indices: Dict,
    match: Optional[Dict[Union[str, Callable], Any]] = None,
    exclude: Optional[Dict[Union[str, Callable], Any]] = None,
):
    for m in match, exclude:
        if m is not None:
            if not isinstance(m, dict):
                raise TypeError("Arguments must be of type dict or None.")
    # input validation -- check that we have an index for all desired lookups
    required_indices = set()
    if match:
        required_indices.update(match.keys())
    if exclude:
        required_indices.update(exclude.keys())
    missing_indices = required_indices.difference(indices)
    if missing_indices:
        raise AttributeNotFoundError


def make_empty_array(dtype: str):
    """Shorthand for making a length-0 numpy array."""
    return np.empty(0, dtype=dtype)


def cyk_intersect(s1: Int64Set, s2: Int64Set) -> Int64Set:
    """Cykhash intersections are faster on small.intersect(big); handle that appropriately.
    https://github.com/realead/cykhash/issues/7"""
    return s1.intersection(s2) if len(s1) < len(s2) else s2.intersection(s1)


def cyk_union(s1: Int64Set, s2: Int64Set) -> Int64Set:
    """Cykhash unions are faster on big.union(small); handle that appropriately.
    https://github.com/realead/cykhash/issues/7"""
    return s1.union(s2) if len(s1) > len(s2) else s2.union(s1)


def filter_vals(attr_vals: Set[Any], expr: Dict[str, Any]) -> Set[Any]:
    """Apply the <, <=, >, >= filters to the attr_vals. Return set of matches."""
    for op, value in expr.items():
        if op in OPERATOR_MAP:
            op = OPERATOR_MAP[op]  # convert 'lt' to '<', etc.
        if op not in ["<", ">", "<=", ">="]:
            raise ValueError(
                f"Invalid operator: {op}. Operator must be one of: {VALID_OPERATORS}."
            )
        if op == "<":
            attr_vals = {v for v in attr_vals if v < value}
        elif op == "<=":
            attr_vals = {v for v in attr_vals if v <= value}
        elif op == ">":
            attr_vals = {v for v in attr_vals if v > value}
        elif op == ">=":
            attr_vals = {v for v in attr_vals if v >= value}
    return attr_vals
