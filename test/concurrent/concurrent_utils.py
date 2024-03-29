import time

import pytest
from ducks.concurrent.main import FAIR
from ducks.concurrent.main import READERS
from ducks.concurrent.main import WRITERS


def slow_wrapper(method):
    """Adds a tiny delay to a method. Good for triggering race conditions that would otherwise be very rare."""

    def wrapped_method(*args):
        time.sleep(0.001)
        return method(*args)

    return wrapped_method


@pytest.fixture(params=[READERS, WRITERS, FAIR])
def priority(request):
    return request.param
