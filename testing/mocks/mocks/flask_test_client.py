import pytest

from app import create_app


@pytest.fixture()
def flask_test_client():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """

    flask_app = create_app()

    # Add a route that raises an error to simulate a 500 response
    @flask_app.route("/test_500")
    def test_500_route():
        raise Exception("This is a simulated 500 error.")

    with flask_app.app_context() as app_context:
        with app_context.app.test_client() as test_client:
            yield test_client
