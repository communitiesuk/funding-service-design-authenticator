from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING

import jwt
from api.responses import error_response
from api.session.exceptions import SessionCreateError
from config import Config
from flask import current_app
from flask import make_response
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask.views import MethodView
from fsd_utils import clear_sentry
from models.magic_link import MagicLinkMethods
from security.utils import create_token
from security.utils import decode_with_options
from security.utils import validate_token

if TYPE_CHECKING:
    from models.account import Account as Account


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
        token = request.cookies.get(Config.FSD_USER_TOKEN_COOKIE_NAME)
        if token:
            try:
                valid_token = validate_token(token)
                return make_response(valid_token), 200
            except jwt.PyJWTError:
                error_response(404, "Session token expired or invalid")
        error_response(404, "No session token found")

    @staticmethod
    def clear_session():
        """
        GET /sessions/sign-out endpoint
        Clears the user session (signing them out)
        Also deletes an existing jwt auth cookie and removes the corresponding
        link records from redis

        Returns: 302 redirect to signed-out page
        """
        fund = None
        round = None
        existing_auth_token = request.cookies.get(
            Config.FSD_USER_TOKEN_COOKIE_NAME
        )
        status = "no_token"
        valid_token = False
        if existing_auth_token:
            # Check if token is valid
            try:
                valid_token = validate_token(existing_auth_token)
                status = "sign_out_request"
            except jwt.ExpiredSignatureError:
                valid_token = decode_with_options(
                    existing_auth_token, options={"verify_exp": False}
                )
                status = "expired_token"
            except jwt.PyJWTError:
                status = "invalid_token"

            # Create query params for signout url if valid token
            fund = valid_token.get("fund")
            round = valid_token.get("round")

            # If validly issued token, clear the redis store
            # of the account and link record
            if valid_token and isinstance(valid_token, dict):
                MagicLinkMethods().clear_existing_user_record(
                    valid_token.get("accountId")
                )

        # Clear the session
        session.clear()
        clear_sentry()

        # Clear the cookie and redirect to signed out page
        signed_out_url = url_for(
            "magic_links_bp.signed_out",
            status=status,
            fund=fund,
            round=round,
        )
        response = make_response(redirect(signed_out_url), 302)
        response.set_cookie(
            Config.FSD_USER_TOKEN_COOKIE_NAME,
            "",
            domain=Config.COOKIE_DOMAIN,
            expires=0,
        )
        return response

    @classmethod
    def create_session_and_redirect(
        cls,
        account: "Account",
        redirect_url: str,
        is_via_magic_link: bool,
        timeout_seconds: int = Config.FSD_SESSION_TIMEOUT_SECONDS,
        fund: str = None,
        round: str = None,
    ):
        """
        Sets a user session token in the client for a given account_id
        and then redirects to a given url
        :param account: The account object of the user we are authenticating
        :param redirect_url: The url to redirect them to after session creation
        :param timeout_seconds: (int, optional)
        The session TTL to set in seconds
        :return: 302 redirect
        """
        try:
            session_details = cls.create_session_details_with_token(
                account,
                is_via_magic_link,
                timeout_seconds=timeout_seconds,
                fund=fund,
                round=round,
            )
            response = make_response(redirect(redirect_url), 302)
            expiry = datetime.now() + timedelta(seconds=timeout_seconds)
            response.set_cookie(
                Config.FSD_USER_TOKEN_COOKIE_NAME,
                session_details["token"],
                domain=Config.COOKIE_DOMAIN,
                expires=expiry,
                secure=Config.SESSION_COOKIE_SECURE,
                samesite=Config.FSD_USER_TOKEN_COOKIE_SAMESITE,
                httponly=Config.SESSION_COOKIE_HTTPONLY,
            )
            current_app.logger.info(
                f"User logged in to account : {account.id}"
            )
            return response
        except SessionCreateError as e:
            error_response(404, str(e))

    @classmethod
    def create_session_details_with_token(
        cls,
        account: "Account",
        is_via_magic_link: bool,
        timeout_seconds: int = Config.FSD_SESSION_TIMEOUT_SECONDS,
        fund: str = None,
        round: str = round,
    ):
        """
        Creates a signed expiring session token for the given account
        :param account: The account object for the user to create a token for
        :param timeout_seconds: The length of the token expiry (or timeout)
        :return: A dict including the signed session token
        """
        session_details = {
            "accountId": account.id,
            "azureAdSubjectId": account.azure_ad_subject_id,
            "email": account.email,
            "fullName": account.full_name,
            "roles": []
            if is_via_magic_link
            and not Config.ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK
            else account.roles,
            "iat": int(datetime.now().timestamp()),
            "exp": int(datetime.now().timestamp() + timeout_seconds),
            "fund": fund,
            "round": round,
        }

        session_details.update({"token": create_token(session_details)})
        session.update(session_details)
        return session_details
