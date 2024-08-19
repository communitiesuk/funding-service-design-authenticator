import pytest
from app import create_app


@pytest.fixture(scope="function")
def flask_test_client():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """

    with create_app(config_name="default").test_client() as test_client:
        yield test_client
