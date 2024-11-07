import pytest
from app import create_app
from config import Config


@pytest.fixture()
def flask_test_client(request: pytest.FixtureRequest, mocker):
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    connexion_args_marker = request.node.get_closest_marker("connexion_args")
    connexion_args = connexion_args_marker.args[0] if connexion_args_marker else {}
    mocker.patch.object(Config, "CONNEXION_OPTIONS", connexion_args)
    with create_app().app_context() as app_context:
        with app_context.app.test_client() as test_client:
            yield test_client
