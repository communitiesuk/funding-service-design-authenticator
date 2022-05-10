"""
Test magic links functionality
"""
import pytest


@pytest.mark.usefixtures("flask_test_client")
@pytest.mark.usefixtures("mock_redis_magic_links")
class TestMagicLinks:

    created_link_keys = []
    used_link_keys = []

    def test_magic_link_is_created(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        an existing h@a.com account in the account_store api
        WHEN we POST to /magic-links/a@example.com
        THEN a magic link is created and returned
        :param flask_test_client:
        """
        expected_link_attributes = {"accountId": "userA"}
        endpoint = "/magic-links/a@example.com"
        response = flask_test_client.post(endpoint)
        magic_link = response.get_json()
        self.created_link_keys.append(magic_link.get("key"))

        assert response.status_code == 201
        assert magic_link.get("accountId") == expected_link_attributes.get(
            "accountId"
        )

    def test_magic_link_redirects(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        an existing magic link
        WHEN we GET /magic-links/{link_key}
        THEN we are redirected to another url
        :param flask_test_client:
        """
        link_key = self.created_link_keys.pop(0)
        use_endpoint = f"/magic-links/{link_key}"
        response = flask_test_client.get(use_endpoint)
        self.used_link_keys.append(link_key)

        assert response.status_code == 302

    def test_reused_magic_link_returns_forbidden(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        a used magic link
        WHEN we GET /magic-links/{link_key}
        THEN we receive a 403 Forbidden response
        :param flask_test_client:
        """
        expected_error = {
            "status": "error",
            "code": 403,
            "message": "Link expired or invalid",
        }
        used_link_key = self.used_link_keys.pop(0)
        reuse_endpoint = f"/magic-links/{used_link_key}"
        response = flask_test_client.get(reuse_endpoint)

        assert response.status_code == 403
        assert response.get_json() == expected_error

    def test_invalid_magic_link_returns_forbidden(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        an invalid magic link
        WHEN we GET /magic-links/{link_key}
        THEN we receive a 403 Forbidden response
        :param flask_test_client:
        """
        expected_error = {
            "status": "error",
            "code": 403,
            "message": "Link expired or invalid",
        }
        use_endpoint = "/magic-links/invalidlink"
        response = flask_test_client.get(use_endpoint)

        assert response.status_code == 403
        assert response.get_json() == expected_error
