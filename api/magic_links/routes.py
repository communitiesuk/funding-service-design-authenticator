import json
from datetime import datetime
from urllib.parse import urlencode, urljoin

from flask import current_app, g, redirect, request, url_for
from flask.views import MethodView
from fsd_utils.authentication.decorators import login_requested

from api.session.auth_session import AuthSessionBase
from common.blueprints import Blueprint
from config import Config
from models.account import AccountMethods
from models.magic_link import MagicLinkMethods

api_magic_link_bp = Blueprint("api_magic_links", __name__)


class MagicLinksView(MagicLinkMethods, MethodView):
    @login_requested
    def get(self, link_id: str):
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
            account = AccountMethods.get_account(account_id=link.get("accountId"))
            if not account:
                current_app.logger.error(
                    "Tried to use magic link for non-existent account_id {account_id}",
                    extra=dict(account_id=link.get("accountId")),
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
                return AuthSessionBase.create_session_and_redirect(
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
            query_params = {k: v for k, v in query_params.items() if v is not None}
            query_string = urlencode(query_params)
            frontend_account_url = urljoin(Config.APPLICANT_FRONTEND_HOST, f"account?{query_string}")
            current_app.logger.warning(
                "The magic link with hash: '{link_hash}' has already been"
                " used but the user with account_id: '{account_id}' is"
                " logged in, redirecting to"
                " '{frontend_account_url}'.",
                extra=dict(link_hash=link_hash, account_id=g.account_id, frontend_account_url=frontend_account_url),
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


api_magic_link_bp.add_url_rule("/magic-links/<link_id>", view_func=MagicLinksView.as_view("use"))
