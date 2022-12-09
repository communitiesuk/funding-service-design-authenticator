from flask import session
from tests.mocks.msal import id_token_claims
from tests.mocks.msal import expected_fsd_user_token_claims
from fsd_utils.authentication.utils import validate_token_rs256


def test_sso_login_redirects_to_ms(flask_test_client):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /sso/login
    THEN we should be redirected to Microsoft Login
    """
    endpoint = "/sso/login"
    expected_redirect = "https://login.microsoftonline.com/"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 302
    assert response.location.startswith(expected_redirect) is True


def test_sso_logout_redirects_to_ms(flask_test_client):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /sso/logout
    THEN we should be redirected to Microsoft Logout
    """
    endpoint = "/sso/logout"
    expected_redirect = (
        "https://login.microsoftonline.com/organizations/oauth2/v2.0/logout"
    )
    response = flask_test_client.get(endpoint)

    assert response.status_code == 302
    assert response.location.startswith(expected_redirect) is True


def test_sso_get_token_returns_404(flask_test_client):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /sso/get-token
    THEN we should receive a 404 "No valid token" message
    """
    endpoint = "/sso/get-token"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 404
    assert response.get_json()["message"] == "No valid token"


def test_sso_get_token_sets_session_and_redirects(
    flask_test_client, mock_msal_client_application
):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /sso/get-token with a valid
        response from azure_ad via the mock_msal_client_application
    THEN we should receive a 302 redirect response with
        the correct claims in the session
    """
    endpoint = "/sso/get-token"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 302
    assert session.get("user") == id_token_claims


def test_sso_get_token_sets_expected_fsd_user_token_cookie_claims(
        flask_test_client, mock_msal_client_application
):
    """
    Args:
        flask_test_client:
        mock_msal_client_application:

    Returns:

    """
    endpoint = "/sso/get-token"
    expected_cookie_name = "fsd_user_token"

    response = flask_test_client.get(endpoint)
    assert response.status_code == 302
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
    valid_token = auth_cookie.value
    credentials = validate_token_rs256(valid_token)
    assert credentials.get("accountId") == expected_fsd_user_token_claims.get("accountId")
    assert credentials.get("azureAdSubjectId") == expected_fsd_user_token_claims.get("azureAdSubjectId")
    assert credentials.get("email") == expected_fsd_user_token_claims.get("email")
    assert credentials.get("fullName") == expected_fsd_user_token_claims.get("fullName")


def test_sso_graphcall_returns_404(flask_test_client, mock_redis_sessions):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /sso/graphcall
    THEN we should be redirected to Microsoft Login
    """
    endpoint = "/sso/graph-call"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 404
    assert response.get_json()["message"] == "No valid token"
