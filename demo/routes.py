import warnings

import config
import msal
import requests
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

demo_bp = Blueprint(
    "demo_bp",
    __name__,
    url_prefix="/",
    template_folder="templates",
)


@demo_bp.route("/", methods=["GET"])
def index():
    if not session.get("user"):
        return redirect(url_for("demo_bp.login"))
    return render_template(
        "demo_index.html", user=session["user"], version=msal.__version__
    )


@demo_bp.route("/login", methods=["GET"])
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = build_auth_code_flow(scopes=config.SCOPE)
    return render_template(
        "login.html",
        auth_url=session["flow"]["auth_uri"],
        version=msal.__version__,
    )


@demo_bp.route(config.REDIRECT_PATH.replace("/auth/msal", ""), methods=["GET"])
# The absolute URL that points here must match
# your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args
        )
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError as e:  # Usually caused by CSRF
        warnings.warn("Value Error on authorized route: " + str(e))
    return redirect(url_for("demo_bp.index"))


@demo_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        config.AUTHORITY
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("demo_bp.index", _external=True)
    )


@demo_bp.route("/graphcall", methods=["GET"])
def graphcall():
    token = _get_token_from_cache(config.SCOPE)
    if not token:
        return redirect(url_for("demo_bp.login"))
    graph_data = requests.get(  # Use token to call downstream service
        config.ENDPOINT,
        headers={"Authorization": "Bearer " + token["access_token"]},
    ).json()
    return render_template("display.html", result=graph_data)


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
        config.CLIENT_ID,
        authority=authority or config.AUTHORITY,
        client_credential=config.CLIENT_SECRET,
        token_cache=cache,
    )


def build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("demo_bp.authorized", _external=True),
    )


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result
