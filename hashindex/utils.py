import numpy as np

from typing import List


def get_field(obj, field):
    if callable(field):
        val = field(obj)
    elif isinstance(obj, dict):
        val = obj.get(field, None)
    else:
        val = getattr(obj, field, None)
    return val


def set_field(obj, field, new_value):
    if callable(field):
        return  # field is derived from some object property, nothing to update
    elif isinstance(obj, dict):
        dict[field] = new_value
    else:
        setattr(obj, field, new_value)


def int_arr():
    """Shorthand function for making an empty int array"""
    return np.array([], dtype="uint64")


def get_attributes(cls) -> List[str]:
    """Helper function to grab the attributes of a class"""
    return list(cls.__annotations__.keys())
