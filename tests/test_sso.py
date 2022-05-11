from flask import session
from tests.mocks.msal import id_token_claims


def test_sso_login_redirects_to_ms(flask_test_client, mock_redis_sessions):
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


def test_sso_logout_redirects_to_ms(flask_test_client, mock_redis_sessions):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /sso/logout
    THEN we should be redirected to Microsoft Logout
    """
    endpoint = "/sso/logout"
    expected_redirect = (
        "https://login.microsoftonline.com/consumers/oauth2/v2.0/logout"
    )
    response = flask_test_client.get(endpoint)

    assert response.status_code == 302
    assert response.location.startswith(expected_redirect) is True


def test_sso_get_token_returns_404(flask_test_client, mock_redis_sessions):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /sso/get-token
    THEN we should receive a 404 "No valid token" message
    """
    endpoint = "/sso/get-token"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 404
    assert response.get_json()["message"] == "No valid token"


def test_sso_get_token_returns_user_claims(
    flask_test_client, mock_redis_sessions, mock_msal_client_application
):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /sso/get-token with a valid session
    THEN we should receive a 200 response with user claims
    """
    endpoint = "/sso/get-token"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 200
    assert response.get_json() == id_token_claims
    assert session.get("user") == id_token_claims


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
