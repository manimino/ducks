import numpy as np

from typing import List, Union, Callable, Optional, Any, Dict, Tuple

from hashbox.exceptions import MissingIndexError, MissingAttribute


def get_field(obj: Any, field: Union[Callable, str]) -> Tuple[Any, bool]:
    """Get the object's attribute value. Return (value, success). Unsuccessful if attribute is missing."""
    if callable(field):
        try:
            val = field(obj)
        except MissingAttribute:
            return None, False
    elif isinstance(obj, dict):
        try:
            val = obj[field]
        except KeyError:
            return None, False
    else:
        try:
            val = getattr(obj, field)
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
        raise MissingIndexError


def make_empty_array(dtype: str):
    return np.empty(0, dtype=dtype)
