import flask


def test_msal_login_redirects_to_ms(flask_test_client):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /auth/msal/login
    THEN we should be redirected to Microsoft Login
    """
    endpoint = "/auth/msal/login"
    expected_redirect = "https://login.microsoftonline.com/"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 302
    assert response.location.startswith(expected_redirect) is True


def test_msal_logout_redirects_to_ms(flask_test_client):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /auth/msal/logout
    THEN we should be redirected to Microsoft Logout
    """
    endpoint = "/auth/msal/logout"
    expected_redirect = "https://login.microsoftonline.com/consumers/oauth2/v2.0/logout"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 302
    assert response.location.startswith(expected_redirect) is True


def test_msal_get_token_returns_404(flask_test_client):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /auth/msal/get-token
    THEN we should receive a 404 "No valid token" message
    """
    endpoint = "/auth/msal/get-token"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 404
    assert response.get_json()["message"] == "No valid token"


# def test_msal_get_token_returns_valid_token(flask_test_client, mocker):
#     """
#     GIVEN We have a functioning Authenticator API
#     WHEN a GET request for /auth/msal/get-token
#     THEN we should receive a 200 response with token
#     """
#     session_mock = mocker.patch.object(flask, "session")
#     mock_token = {"mock": "token"}
#     session_mock.get.return_value = {"user": mock_token}
#     endpoint = "/auth/msal/get-token"
#     response = flask_test_client.get(endpoint)
#
#     assert response.status_code == 404
#     assert response.get_json()["mock"] == "token"


def test_msal_graphcall_returns_404(flask_test_client):
    """
    GIVEN We have a functioning Authenticator API
    WHEN a GET request for /auth/msal/graphcall
    THEN we should be redirected to Microsoft Login
    """
    endpoint = "/auth/msal/graphcall"
    response = flask_test_client.get(endpoint)

    assert response.status_code == 404
    assert response.get_json()["message"] == "No valid token"



