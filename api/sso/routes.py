import warnings

import msal
import requests
from config.env import env
from flask import redirect
from flask import request
from flask import session
from flask.views import MethodView


class SsoView(MethodView):
    def login(self):
        # Technically we could use empty list [] as scopes to do just sign in,
        # here we choose to also collect end user consent upfront
        session["flow"] = self.build_auth_code_flow(
            scopes=env.config.get("SCOPE")
        )
        return redirect(session["flow"]["auth_uri"]), 302

    def logout(self):
        post_logout_redirect_uri = request.args.get(
            "post_logout_redirect_uri", ""
        )
        session.clear()  # Wipe out user and its token cache from session
        return redirect(  # Also logout from your tenant's web session
            env.config.get("AUTHORITY")
            + "/oauth2/v2.0/logout"
            + "?post_logout_redirect_uri="
            + post_logout_redirect_uri
        )

    def get_token(self):
        # The absolute URL that points here must match
        # your app's redirect_uri set in AAD
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
            return session["user"], 200
        except ValueError as e:  # Usually caused by CSRF
            warnings.warn("Value Error on get_token route: " + str(e))
        return {"message": "No valid token"}, 404

    def graphcall(self):
        token = self._get_token_from_cache(env.config.get("SCOPE"))
        if not token:
            return {"message": "No valid token"}, 404
        graph_data = requests.get(  # Use token to call downstream service
            env.config.get("ENDPOINT"),
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
            env.config.get("CLIENT_ID"),
            authority=authority or env.config.get("AUTHORITY"),
            client_credential=env.config.get("CLIENT_SECRET"),
            token_cache=cache,
        )

    def build_auth_code_flow(self, authority=None, scopes=None):
        return self._build_msal_app(
            authority=authority
        ).initiate_auth_code_flow(
            scopes or [], redirect_uri=env.config.get("REDIRECT_URI")
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
