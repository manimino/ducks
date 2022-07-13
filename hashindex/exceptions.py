class FrozenError(Exception):
    """Raised when attempting to modify a FrozenIndex"""

    pass


class MissingIndexError(Exception):
    """Raised when querying a field we don't have an index for"""

    pass


class MissingValueError(Exception):
    """Raised when adding an object that is missing a field we need to index"""

    pass


class MissingObjectError(Exception):
    """Raised when removing or updating an object we don't have."""
    pass


class ImmutableUpdateError(Exception):
    """Raised when someone attempts to update an immutable object such as a string."""
    pass
