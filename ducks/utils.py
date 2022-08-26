import numpy as np

from typing import List, Union, Callable, Optional, Any, Dict, Tuple

from cykhash import Int64Set

from ducks.constants import ANY, VALID_OPERATORS, OPERATOR_MAP, EXCLUDE_OPERATORS
from ducks.exceptions import AttributeNotFoundError, MissingAttribute


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


def split_query(query: Dict) -> Tuple[Dict, Dict]:
    """Split query into match and exclude terms"""
    match_query = dict()
    exclude_query = dict()
    for attr, expr in query.items():
        match_expr = dict()
        exclude_expr = dict()
        for op, val in expr.items():
            if op in EXCLUDE_OPERATORS:
                # invert "not in" -> "in", etc.
                exclude_expr[EXCLUDE_OPERATORS[op]] = val
            else:
                match_expr[op] = val
        if match_expr:
            match_query[attr] = match_expr
        if exclude_expr:
            exclude_query[attr] = exclude_expr
    return match_query, exclude_query


def standardize_expr(expr: Any) -> Dict:
    """Turn a find() expr into a dict of {operator: value}."""
    if isinstance(expr, dict):
        return validate_and_standardize_operators(expr)
    if isinstance(expr, list):
        return {"in": expr}
    if isinstance(expr, set) and expr is not ANY:
        raise ValueError(f"Expression {expr} is a set. Did you mean to make a dict?")
    # otherwise, it's a value
    return {"==": expr}


def validate_and_standardize_operators(expr: Dict) -> Dict:
    std_expr = {}
    for op, val in expr.items():
        if op in OPERATOR_MAP:
            std_expr[OPERATOR_MAP[op]] = val
        else:
            std_expr[op] = val
    for op in std_expr:
        if op not in VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator: {op}. Operator must be one of: {VALID_OPERATORS}."
            )
    if "<" in std_expr and "<=" in std_expr:
        raise ValueError(f"Either '<' or '<=' may be used in {expr}, not both.")
    if ">" in std_expr and ">=" in std_expr:
        raise ValueError(f"Either '>' or '>=' may be used in {expr}, not both.")
    return std_expr


def validate_query(
    indexes: Dict,
    match: Optional[Dict[Union[str, Callable], Any]] = None,
    exclude: Optional[Dict[Union[str, Callable], Any]] = None,
):
    # input validation -- check that we have an index for all desired lookups
    required_indexes = set()
    if match:
        required_indexes.update(match.keys())
    if exclude:
        required_indexes.update(exclude.keys())
    missing_indexes = required_indexes.difference(indexes)
    if missing_indexes:
        raise AttributeNotFoundError(
            f"Cannot find on: {list(missing_indexes)}. Attributes must be specified on creation."
        )


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
