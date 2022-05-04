from datetime import datetime

import jwt
from api.session.exceptions import SessionCreateError
from config.env import env
from flask import abort
from flask import make_response
from flask import redirect
from flask import request
from flask import session
from flask.views import MethodView
from security.utils import create_token
from security.utils import validate_token


class AuthSessionView(MethodView):
    @staticmethod
    def user():
        token = request.cookies.get(
            env.config.get("FSD_USER_TOKEN_COOKIE_NAME")
        )
        if token:
            try:
                valid_token = validate_token(token)
                return make_response(valid_token), 200
            except jwt.PyJWTError as e:
                # abort(404, "Session token expired or invalid")
                abort(404, str(e))
        abort(404, "No session token found")

    @classmethod
    def create_session_and_redirect(cls, account_id: str, redirect_url: str):
        try:
            session_details = cls.create_session_details_with_token(account_id)
            response = make_response(redirect(redirect_url), 302)
            response.set_cookie(
                env.config.get("FSD_USER_TOKEN_COOKIE_NAME"),
                session_details["token"],
            )
            return response
        except SessionCreateError as e:
            abort(404, str(e))

    @classmethod
    def create_session_details_with_token(cls, account_id: str):
        session_details = {
            "accountId": account_id,
            "iat": int(datetime.now().timestamp()),
            "exp": int(
                datetime.now().timestamp()
                + env.config.get("FSD_SESSION_TIMEOUT_SECS", 0)
            ),
        }

        session_details.update({"token": create_token(session_details)})
        session.update(session_details)
        return session_details
