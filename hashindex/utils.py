import numpy as np


def get_field(obj, field):
    if callable(field):
        val = field(obj)
    elif isinstance(obj, dict):
        val = obj.get(field, None)
    else:
        val = getattr(obj, field, None)
    return val


def int_arr():
    """Shorthand function for making an empty int array"""
    return np.array([], dtype="uint64")
