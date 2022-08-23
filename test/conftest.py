import pytest
from dbox import DBox, FrozenDBox, ConcurrentDBox


@pytest.fixture(params=[DBox, FrozenDBox, ConcurrentDBox])
def box_class(request):
    return request.param


class AssertRaises:
    """
    While the unittest package has an assertRaises context manager, it is incompatible with pytest + fixtures.
    Cleaner to just implement an AssertRaises here.
    """

    def __init__(self, exc_type):
        self.exc_type = exc_type

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, exception_traceback):
        assert exception_type == self.exc_type
        return True  # suppress the exception


class BadHash:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return 42

    def __eq__(self, other):
        return self.n == other.n

    def __repr__(self):
        return str(self.n)

    def __lt__(self, other):
        return self.n < other.n


class TwoHash:
    def __init__(self, n):
        self.n = n

    def __hash__(self):
        return self.n % 2

    def __lt__(self, other):
        return self.n < other.n
