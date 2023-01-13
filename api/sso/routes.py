import warnings

import msal
import requests
from api.session.auth_session import AuthSessionView
from config import Config
from flask import make_response
from flask import redirect
from flask import request
from flask import session
from flask.views import MethodView
from fsd_utils import clear_sentry
from models.account import AccountMethods


class SsoView(MethodView):
    def login(self):
        """
        GET /sso/login endpoint
        Redirects to the Azure AD auth uri
        :return: 302 redirect to Microsoft Login
        """
        session["flow"] = self.build_auth_code_flow(
            scopes=Config.MS_GRAPH_PERMISSIONS_SCOPE
        )
        return redirect(session["flow"]["auth_uri"]), 302

    def logout(self):
        """
        GET /sso/logout endpoint
        Clears the user session then redirects to
        Azure AD logout endpoint to logout from our tenants web session too
        :return:
        """
        post_logout_redirect_uri = request.args.get(
            "post_logout_redirect_uri", Config.SSO_POST_SIGN_OUT_URL
        )
        azure_ad_sign_out_url = (
            Config.AZURE_AD_AUTHORITY
            + "/oauth2/v2.0/logout"
            + "?post_logout_redirect_uri="
            + post_logout_redirect_uri
        )
        session.clear()
        response = make_response(redirect(azure_ad_sign_out_url), 302)
        response.set_cookie(
            Config.FSD_USER_TOKEN_COOKIE_NAME,
            "",
            domain=Config.COOKIE_DOMAIN,
            expires=0,
        )
        clear_sentry()
        return response

    def get_token(self):
        """
        GET /sso/get-token
        The endpoint that Azure AD redirects back to
        after successful authentication.
        Validates args from return request and if claims validated,
        then creates a user property on the session with token claims
        # NOTE: The absolute URL that points here must match
        # this app's redirect_uri set in Azure AD
        :return: 200 json of valid user token claims or 404 on error
        """
        try:
            cache = self._load_cache()
            result = self._build_msal_app(
                cache=cache
            ).acquire_token_by_auth_code_flow(
                session.get("flow", {}), request.args
            )
            if "error" in result:
                return result, 500
            session["user"] = result.get("id_token_claims")
            self._save_cache(cache)
        except ValueError as e:  # Usually caused by CSRF
            warnings.warn(f"Value Error on get_token route: {str(e)}")

        if "user" not in session or not session["user"].get("sub"):
            return {"message": "No valid token"}, 404

        updated_account = AccountMethods.create_or_update_account(
            azure_ad_subject_id=session["user"].get("sub"),
            email=session["user"].get("preferred_username"),
            full_name=session["user"].get("name"),
            roles=session["user"].get("roles"),
        )

        # Create session token, set cookie and redirect
        return AuthSessionView.create_session_and_redirect(
            account=updated_account,
            redirect_url=Config.ASSESSMENT_POST_LOGIN_URL,
            timeout_seconds=Config.FSD_ASSESSMENT_SESSION_TIMEOUT_SECONDS,
        )

    def graph_call(self):
        """
        GET /sso/graph-call endpoint
        Shows the graph object for the current authenticated user
        Requires a valid token in the session
        :return: 200 json of user graph data or 404 not found
        """
        token = self._get_token_from_cache(Config.MS_GRAPH_PERMISSIONS_SCOPE)
        if not token:
            return {"message": "No valid token"}, 404
        graph_data = requests.get(  # Use token to call downstream service
            Config.MS_GRAPH_ENDPOINT,
            headers={"Authorization": "Bearer " + token["access_token"]},
        ).json()
        return graph_data, 200

    @staticmethod
    def _load_cache():
        cache = msal.SerializableTokenCache()
        if session.get("token_cache"):
            cache.deserialize(session["token_cache"])
        return cache

    @staticmethod
    def _save_cache(cache):
        if cache.has_state_changed:
            session["token_cache"] = cache.serialize()

    @staticmethod
    def _build_msal_app(cache=None, authority=None):
        return msal.ConfidentialClientApplication(
            Config.AZURE_AD_CLIENT_ID,
            authority=authority or Config.AZURE_AD_AUTHORITY,
            client_credential=Config.AZURE_AD_CLIENT_SECRET,
            token_cache=cache,
        )

    def build_auth_code_flow(self, authority=None, scopes=None):
        return self._build_msal_app(
            authority=authority
        ).initiate_auth_code_flow(
            scopes or [], redirect_uri=Config.AZURE_AD_REDIRECT_URI
        )

    def _get_token_from_cache(self, scope=None):
        cache = (
            self._load_cache()
        )  # This web app maintains one cache per session
        cca = self._build_msal_app(cache=cache)
        accounts = cca.get_accounts()
        if accounts:  # So all account(s) belong to the current signed-in user
            result = cca.acquire_token_silent(scope, account=accounts[0])
            self._save_cache(cache)
            return result
