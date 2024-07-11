from unittest import mock

import pytest
from app import create_app
from config import Config


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
        assert response.json == expected_dict, "Unexpected json body"

    @mock.patch.object(Config, "CONNEXION_OPTIONS", {})
    def test_swagger_ui_not_published(self):
        with create_app().app_context() as app_context:
            with app_context.app.test_client() as test_client:
                use_endpoint = "/docs"
                response = test_client.get(use_endpoint, follow_redirects=True)
                assert response.status_code == 404

    @mock.patch.object(Config, "CONNEXION_OPTIONS", {"swagger_url": "/docs"})
    def test_swagger_ui_is_published(self):
        with create_app().app_context() as app_context:
            with app_context.app.test_client() as test_client:
                use_endpoint = "/docs"
                response = test_client.get(use_endpoint, follow_redirects=True)
                assert response.status_code == 200
