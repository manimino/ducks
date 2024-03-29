import pytest
from ducks import ConcurrentDex
from ducks import Dex
from ducks import FrozenDex


@pytest.fixture(params=[Dex, FrozenDex, ConcurrentDex])
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


class Attr:
    def __init__(self, n: int):
        self.n = n

    def __hash__(self):
        return self.n

    def __eq__(self, other):
        return self.n == other.n

    def __repr__(self):
        return str(self.n)

    def __lt__(self, other):
        return self.n < other.n
