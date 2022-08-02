class FrozenError(Exception):
    """Raised when attempting to modify a FrozenHashBox"""


class AttributeNotFoundError(Exception):
    """Raised when querying an attribute we don't have"""


class MissingAttribute(Exception):
    """Raise this in your attribute functions to denote that the object is missing this attribute. Finds that
    match the attribute will never return this object. Finds that exclude the attribute will."""
