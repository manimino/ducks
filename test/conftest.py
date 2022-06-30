import pytest


@pytest.fixture(params=[True, False])
def freeze(request):
    return request.param
