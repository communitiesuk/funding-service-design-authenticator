import json
import urllib.parse
from datetime import datetime

from api.responses import error_response
from api.responses import magic_link_201_response
from api.session.auth_session import AuthSessionView
from config import Config
from flask import current_app
from flask import g
from flask import redirect
from flask import request
from flask import url_for
from flask.views import MethodView
from fsd_utils.authentication.decorators import login_requested
from models.account import AccountMethods
from models.magic_link import MagicLinkError
from models.magic_link import MagicLinkMethods


class MagicLinksView(MagicLinkMethods, MethodView):
    @login_requested
    def use(self, link_id: str):
        """
        GET /magic-links/{link_id} endpoint
        If the link_id matches a valid link key, this then:
        - creates a session,
        - sets a session_id cookie in the client
        - sets a session_token cookie in the client
        - deletes the link record from redis
        - deletes the user record from redis
        - then finally, redirects to the redirect_url
        If no matching valid link is found returns a 404 error message
        :param link_id: String short key for the link
        :return: 302 Redirect / 404 Error
        """

        fund_short_name = request.args.get("fund")
        round_short_name = request.args.get("round")

        link_key = ":".join([Config.MAGIC_LINK_RECORD_PREFIX, link_id])
        link_hash = self.redis_mlinks.get(link_key)
        if link_hash:
            link = json.loads(link_hash)
            user_key = ":".join(
                [
                    Config.MAGIC_LINK_USER_PREFIX,
                    link.get("accountId"),
                ]
            )
            self.redis_mlinks.delete(link_key)
            self.redis_mlinks.delete(user_key)

            # Check account exists
            account = AccountMethods.get_account(
                account_id=link.get("accountId")
            )
            if not account:
                current_app.logger.error(
                    "Tried to use magic link for "
                    f"non-existent account_id {link.get('accountId')}"
                )
                redirect(
                    url_for(
                        "magic_links_bp.invalid",
                        fund=fund_short_name,
                        round=round_short_name,
                    )
                )

            # Check link is not expired
            if link.get("exp") > int(datetime.now().timestamp()):
                return AuthSessionView.create_session_and_redirect(
                    account=account,
                    is_via_magic_link=True,
                    redirect_url=link.get("redirectUrl"),
                    fund=fund_short_name,
                    round=round_short_name,
                )
            return redirect(
                url_for(
                    "magic_links_bp.invalid",
                    error="Link expired",
                    fund=fund_short_name,
                    round=round_short_name,
                )
            )

        elif g.is_authenticated:
            # else if no link exists (or it has been used)
            # but the user is already logged in
            # then redirect them to the global redirect url
            query_params = {
                "fund": fund_short_name,
                "round": round_short_name,
            }
            query_params = {
                k: v for k, v in query_params.items() if v is not None
            }
            query_string = urllib.parse.urlencode(query_params)
            frontend_account_url = (
                f"{Config.MAGIC_LINK_REDIRECT_URL}?{query_string}"
            )
            current_app.logger.warn(
                f"The magic link with hash: '{link_hash}' has already been"
                f" used but the user with account_id: '{g.account_id}' is"
                " logged in, redirecting to"
                f" '{frontend_account_url}'."
            )
            return redirect(frontend_account_url)
        return redirect(
            url_for(
                "magic_links_bp.invalid",
                error="Link expired",
                fund=fund_short_name,
                round=round_short_name,
            )
        )

    def create(self):
        """
        Creates a magic link for an existing account holder
        :param email: the account holders email address
        :param redirect_url: the url the link should redirect to
        :return: a json of the magic link created (or an error of failure)
        """
        email = request.get_json().get("email")
        redirect_url = request.get_json().get("redirectUrl")
        if not email:
            return error_response(400, "Email is required")
        account = AccountMethods.get_account(email)
        if account:
            try:
                new_link_json = self.create_magic_link(account, redirect_url)
                return magic_link_201_response(new_link_json)
            except MagicLinkError:
                return error_response(500, "Could not create a unique link")
        return error_response(401, "Account does not exist")
