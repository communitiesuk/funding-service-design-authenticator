import pytest


class TestHealthchecks:
    @pytest.mark.usefixtures("mock_redis_magic_links")
    def testChecks(self, flask_test_client):
        response = flask_test_client.get("/healthcheck")
        expected_dict = {
            "checks": [{"check_flask_running": "OK"}, {"check_redis": "OK"}]
        }
        assert response.status_code == 200, "Unexpected response code"
        assert response.json == expected_dict, "Unexpected json body"
