import pytest
from app import create_app


@pytest.fixture()
def flask_test_client_no_ui():
    """
    Creates the test client with the Swagger UI disabled.
    """
    with create_app(config_name="no_ui").test_client() as test_client:
        yield test_client
