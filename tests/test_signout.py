"""
Test magic links functionality
"""
import pytest
from security.utils import create_token
from security.utils import validate_token


@pytest.mark.usefixtures("flask_test_client")
@pytest.mark.usefixtures("mock_redis_magic_links")
class TestSignout:

    created_link_keys = []
    used_link_keys = []
    valid_token = ""

    def test_signout_checks_for_cookie(self, flask_test_client):
        """
        GIVEN a running Flask client
        WHEN we issue a GET to /sessions/sign-out
        THEN the endpoint checks for existing auth cookie
        :param flask_test_client:
        """
        endpoint = "/sessions/sign-out"
        response = flask_test_client.get(endpoint)

        assert response.status_code == 302
        assert response.location == "/service/magic-links/signed-out/no_token"

    def test_signout_clears_cookie(self, flask_test_client):
        """
        GIVEN a running Flask client
        WHEN we issue a GET to /sessions/sign-out
        with an existing invalid "fsd_user_token" auth cookie
        THEN the endpoint clears the cookie
        :param flask_test_client:
        """
        endpoint = "/sessions/sign-out"
        flask_test_client.set_cookie("/", "fsd_user_token", "invalid_token")
        response = flask_test_client.get(endpoint)

        assert response.status_code == 302
        assert (
            "fsd_user_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/"
            in response.headers.get("Set-Cookie")
        )
        assert (
            response.location
            == "/service/magic-links/signed-out/invalid_token"
        )

    def test_magic_link_auth_can_be_signed_out(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        and a valid magic link has been clicked and a valid
        jwt auth token set
        WHEN we issue a get to /sessions/sign-out
        THEN the token is cleared and the user signed out
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

        # Check user can sign out
        endpoint = "/sessions/sign-out"
        response = flask_test_client.get(endpoint)
        assert response.status_code == 302
        assert (
            "fsd_user_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/"
            in response.headers.get("Set-Cookie")
        )
        assert (
            response.location
            == "/service/magic-links/signed-out/sign_out_request"
        )

    def test_user_page_for_logged_out_user(self, flask_test_client):
        """
        GIVEN a running Flask client and user is not logged in
        WHEN we access the user page
        THEN the user page is displayed
        :param flask_test_client:
        """
        endpoint = "/service/user"
        response = flask_test_client.get(endpoint)
        assert response.status_code == 200
        assert (
            """<p class="govuk-body">You are not logged in.</p>"""
            in response.get_data(as_text=True)
        )
        assert (
            """<a href="/sso/login" role="button" draggable="false" class="govuk-button" data-module="govuk-button">\n  Sign in\n</a>"""  # noqa
            in response.get_data(as_text=True)
        )

    def test_user_page_with_missing_roles(self, flask_test_client):
        """
        GIVEN a running Flask client, user is logged in but does not
        have the required roles
        WHEN we access the user page
        THEN the roles required error is shown on the user page
        :param flask_test_client:
        """

        test_payload = {
            "accountId": "test-user",
            "email": "test@example.com",
            "fullName": "Test User",
            "roles": ["LEAD_ASSESSOR", "ASSESSOR", "COMMENTER"],
        }

        token = create_token(test_payload)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        endpoint = (
            "/service/user?roles_required=ultimate_assessor|mega_assessor"
        )
        response = flask_test_client.get(endpoint)
        assert response.status_code == 200
        assert (
            """<p class="govuk-body">You do not have access as your account does not have the right permissions set up."""  # noqa
            in response.get_data(as_text=True)
        )
        assert (
            """<p class="govuk-body">Please email the support mailbox"""  # noqa
            in response.get_data(as_text=True)
        )
        assert (
            """<a href="/sso/login" role="button" draggable="false" class="govuk-button" data-module="govuk-button">\n  Sign in\n</a>"""  # noqa
            not in response.get_data(as_text=True)
        )

    def test_user_page_with_correct_roles(self, flask_test_client):
        """
        GIVEN a running Flask client, user is logged in and
        has the required roles
        WHEN we access the user page
        THEN the user page is displayed with option to sign out
        :param flask_test_client:
        """

        test_payload = {
            "accountId": "test-user",
            "email": "test@example.com",
            "fullName": "Test User",
            "roles": ["LEAD_ASSESSOR", "ASSESSOR", "COMMENTER"],
        }

        token = create_token(test_payload)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        endpoint = "/service/user?roles_required=assessor|commenter"
        response = flask_test_client.get(endpoint)
        assert response.status_code == 200
        assert (
            """<a href="/sso/logout" role="button" draggable="false" class="govuk-button" data-module="govuk-button">\n  Sign out\n</a>"""  # noqa
            in response.get_data(as_text=True)
        )
