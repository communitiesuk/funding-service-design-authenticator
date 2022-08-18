class TestHealthchecks:
    def testFlaskRunning(self, flask_test_client):
        response = flask_test_client.get("/healthcheck")
        expected_dict = {"checks":[{"check_running":"OK"}]}
        assert response.status_code == 200, "Unexpected response code"
        assert response.json == expected_dict, "Unexpected json body"