import numpy as np

from typing import List, Union, Callable, Optional, Any, Dict, Tuple

from hashbox import ANY
from hashbox.exceptions import AttributeNotFoundError, MissingAttribute


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
