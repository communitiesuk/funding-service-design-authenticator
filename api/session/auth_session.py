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
    """
    Views for session related operations
    """

    @staticmethod
    def user():
        """
        GET /sessions/user endpoint
        Shows the user details of the current user session
        or an error if no authenticated user session found
        :return: 200 user details json or 404 error
        """
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
        """
        Sets a user session token in the client for a given account_id
        and then redirects to a given url
        :param account_id: The account_id of the user we are authenticating
        :param redirect_url: The url to redirect them to after session creation
        :return: 302 redirect
        """
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
        """
        Creates a signed expiring session token for the given account_id
        :param account_id: The account_id for the user to create a token for
        :return: A dict including the signed session token
        """
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
