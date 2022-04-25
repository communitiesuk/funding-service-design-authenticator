import requests
from flask import session, request, redirect, url_for
import msal
import config
import warnings


def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = build_auth_code_flow(scopes=config.SCOPE)
    return redirect(session["flow"]["auth_uri"]), 302


def logout():
    post_logout_redirect_uri = request.args.get("post_logout_redirect_uri", "")
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + post_logout_redirect_uri)


# The absolute URL that points here must match your app's redirect_uri set in AAD
def get_token():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return result, 500
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
        return session["user"], 200
    except ValueError as e:  # Usually caused by CSRF
        warnings.warn('Get Token Value Error: ' + str(e))
    return {"message": "No valid token"}, 404


def graphcall():
    token = _get_token_from_cache(config.SCOPE)
    if not token:
        return {"message": "No valid token"}, 404
    graph_data = requests.get(  # Use token to call downstream service
        config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return graph_data, 200


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        config.CLIENT_ID, authority=authority or config.AUTHORITY,
        client_credential=config.CLIENT_SECRET, token_cache=cache)


def build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=config.REDIRECT_URI)


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result
