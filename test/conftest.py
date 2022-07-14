import pytest
from hashindex import HashIndex, FrozenHashIndex


@pytest.fixture(params=[HashIndex, FrozenHashIndex])
def index_type(request):
    return request.param
