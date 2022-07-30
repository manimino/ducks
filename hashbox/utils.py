import numpy as np

from typing import List, Union, Callable, Optional, Any, Dict
from hashbox.exceptions import MissingIndexError


def get_field(obj, field):
    if callable(field):
        val = field(obj)
    elif isinstance(obj, dict):
        val = obj.get(field, None)
    else:
        val = getattr(obj, field, None)
    return val


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
