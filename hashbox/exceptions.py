class FrozenError(Exception):
    """Raised when attempting to modify a FrozenIndex"""


class MissingIndexError(Exception):
    """Raised when querying a field we don't have an index for"""


class MissingAttribute(Exception):
    """Raise this in your attribute functions to denote that the object is missing this attribute. Finds that
    match the attribute will never return this object. Finds that exclude the attribute will."""
