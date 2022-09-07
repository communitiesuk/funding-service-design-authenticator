"""
Test magic links functionality
"""
import pytest
from security.utils import validate_token


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
        expected_link_attributes = {"accountId": "usera"}
        payload = {
            "email": "a@example.com",
            "redirectUrl": "https://example.com/redirect-url",
        }
        endpoint = "/magic-links"
        response = flask_test_client.post(endpoint, json=payload)
        magic_link = response.get_json()
        self.created_link_keys.append(magic_link.get("key"))

        assert response.status_code == 201
        assert magic_link.get("accountId") == expected_link_attributes.get(
            "accountId"
        )

    def test_magic_link_redirects_to_landing(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        an existing magic link
        WHEN we GET /magic-links/landing/{link_key} to the API
        THEN we are redirected to the frontend landing page
        (without using the single use magic token)
        :param flask_test_client:
        """
        link_key = self.created_link_keys.pop(0)
        self.created_link_keys.append(link_key)
        use_endpoint = f"/magic-links/landing/{link_key}"
        response = flask_test_client.get(use_endpoint)
        self.used_link_keys.append(link_key)

        assert response.status_code == 302

    def test_magic_link_sets_auth_cookie(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        an existing magic link
        WHEN we GET /magic-links/{link_key}
        THEN we are redirected to another url (the application service)
        :param flask_test_client:
        """
        link_key = self.created_link_keys.pop(0)
        self.created_link_keys.append(link_key)
        use_endpoint = f"/magic-links/{link_key}"
        response = flask_test_client.get(use_endpoint)
        self.used_link_keys.append(link_key)

        assert "fsd_user_token" in response.headers.get("Set-Cookie")

    def test_magic_link_sets_valid_cookie_token(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        and a valid magic link
        WHEN we issue a get to /magic-links/{LINK_KEY}
        THEN a valid token is created
        :param flask_test_client:
        """
        expected_account_id = "usera"
        expected_cookie_name = "fsd_user_token"
        magic_link_create_payload = {
            "email": "a@example.com",
            "redirectUrl": "https://example.com/redirect-url",
        }
        endpoint = "/magic-links"
        response = flask_test_client.post(
            endpoint, json=magic_link_create_payload
        )
        magic_link = response.get_json()
        link_key = magic_link.get("key")
        self.created_link_keys.append(link_key)
        use_endpoint = f"/magic-links/{link_key}"
        flask_test_client.get(use_endpoint)
        flask_test_client.get(use_endpoint)
        self.used_link_keys.append(link_key)
        auth_cookie = next(
            (
                cookie
                for cookie in flask_test_client.cookie_jar
                if cookie.name == expected_cookie_name
            ),
            None,
        )

        # Check auth token cookie is set and is valid
        assert auth_cookie is not None, (
            f"Auth cookie '{expected_cookie_name}' was expected to be set, but"
            " could not be found"
        )
        self.valid_token = auth_cookie.value
        credentials = validate_token(self.valid_token)
        assert credentials.get("accountId") == expected_account_id

    def test_magic_link_redirects(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        an existing magic link
        WHEN we GET /magic-links/{link_key}
        THEN we are redirected to another url (the application service)
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
        used_link_key = self.used_link_keys.pop(0)
        reuse_endpoint = f"/magic-links/{used_link_key}"
        response = flask_test_client.get(reuse_endpoint, follow_redirects=True)

        assert response.status_code == 403
        assert b"Link expired" in response.data

    def test_invalid_magic_link_returns_forbidden(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        an invalid magic link
        WHEN we GET /magic-links/{link_key}
        THEN we receive a 403 Forbidden response
        :param flask_test_client:
        """
        use_endpoint = "/magic-links/invalidlink"
        response = flask_test_client.get(use_endpoint, follow_redirects=True)

        assert response.status_code == 403
        assert b"Link expired" in response.data
