class FrozenError(Exception):
    """Raised when attempting to modify a FrozenIndex"""

    pass


class MissingIndexError(Exception):
    """Raised when querying a field we don't have an index for"""

    pass
