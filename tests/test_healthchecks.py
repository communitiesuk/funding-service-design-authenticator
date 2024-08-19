import pytest
from app import create_app


@pytest.fixture(scope="session")
def app():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    app = create_app()
    yield app.app


@pytest.mark.app(debug=False)
def test_app(app):
    assert not app.debug, "Ensure the app not in debug mode"


class TestHealthchecks:
    @pytest.mark.usefixtures("mock_redis_magic_links")
    def testChecks(self, flask_test_client):
        response = flask_test_client.get("/healthcheck")
        expected_dict = {
            "checks": [{"check_flask_running": "OK"}, {"check_redis": "OK"}],
            "version": "abc123",
        }
        assert response.status_code == 200, "Unexpected response code"
        assert response.json() == expected_dict, "Unexpected json body"

    def test_swagger_ui_not_published(self, flask_test_client_no_ui):
        use_endpoint = "/ui"
        response = flask_test_client_no_ui.get(use_endpoint, follow_redirects=True)
        assert response.status_code == 404

    def test_swagger_ui_is_published(self, flask_test_client):
        use_endpoint = "/ui"
        response = flask_test_client.get(use_endpoint, follow_redirects=True)
        assert response.status_code == 200
