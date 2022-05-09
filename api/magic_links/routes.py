import json
import random
import string
from datetime import datetime
from datetime import timedelta

from api.responses import error_response
from api.responses import magic_link_201_response
from api.session.auth_session import AuthSessionView
from api.session.data import get_account
from api.session.models.account import Account
from config.env import env
from flask import Response
from flask.views import MethodView
from flask_redis import FlaskRedis
from security.utils import create_token


class MagicLinksView(MethodView):
    @property
    def redis_mlinks(self) -> FlaskRedis:
        """
        A FlaskRedis client connection to the magic links redis instance
        :return: FlaskRedis instance
        """
        from app import redis_mlinks

        return redis_mlinks

    @property
    def _links(self):
        """
        All magic link keys as a list, for the search endpoint
        :return: A list of keys from the magic links redis instance
        """
        links = [link.decode("utf-8") for link in self.redis_mlinks.keys("*")]
        return links

    @staticmethod
    def _make_short_key():
        """
        Creates a short string to act as the magic link key
        :return: Random string
        """
        letters = string.ascii_letters
        return "".join(random.choice(letters) for i in range(8))

    @staticmethod
    def _make_link_json(account: Account, redirect_url: str):
        """
        Creates a json dict of minimal link claims and generates a
        signed token of those claims and adds the token as value
        on the returned dict
        :param account: An Account object holding the user's details
        :param redirect_url: String url to redirect to
        :return: A dictionary containing the link claims and signed token
        """
        new_link_json = {
            "accountId": account.id,
            "iat": int(datetime.now().timestamp()),
            "exp": int(
                (
                    datetime.now()
                    + timedelta(
                        days=env.config.get("MAGIC_LINK_EXPIRY_DAYS", 0),
                        minutes=1,
                    )
                ).timestamp()
            ),
            "redirectUrl": redirect_url,
        }
        new_link_json.update({"token": create_token(new_link_json)})
        return new_link_json

    def _set_unique_keyed_record(self, value) -> str | None:
        """
        Attempts to save the link claims with a unique short key
        that doesn't already exist (and returns None if it fails)
        :param value: A json dictionary of link attributes
        :return: The unique short key for the link hash (or None)
        """
        key = self._make_short_key()
        created = self.redis_mlinks.setex(
            key, env.config.get("MAGIC_LINK_EXPIRY_SECONDS", 0), value
        )
        if created == 1:
            return key

    def search(self):
        """
        GET /magic-links endpoint
        :return: Json Response
        """
        return Response(json.dumps(self._links), mimetype="application/json")

    def use(self, link_id: str):
        """
        GET /magic-links/{link_id} endpoint
        If the link_id matches a valid link key, this then:
        - creates a session,
        - sets a session_id cookie in the client
        - sets a session_token cookie in the client
        - deletes the link record from redis
        - then finally, redirects to the redirect_url
        If no matching valid link is found returns a 404 error message
        :param link_id: String short key for the link
        :return: 302 Redirect / 404 Error
        """
        link_hash = self.redis_mlinks.get(link_id)
        if link_hash:
            link = json.loads(link_hash)
            self.redis_mlinks.delete(link_id)

            # Check link is not expired
            if link.get("exp") > int(datetime.now().timestamp()):
                return AuthSessionView.create_session_and_redirect(
                    account_id=link.get("accountId"),
                    redirect_url=link.get("redirectUrl"),
                )
            return error_response(404, "Link expired")
        return error_response(404, "Link expired or invalid")

    def create(self, email: str, redirect_url: str = "https://google.com"):
        """
        Creates a magic link for an existing account holder
        :param email: the account holders email address
        :param redirect_url: the url the link should redirect to
        :return: a json of the magic link created (or an error of failure)
        """
        account = get_account(email)
        if account:
            new_link_json = self._make_link_json(account, redirect_url)

            # Try up to 6 times to create a unique short key for the link
            # which doesn't already exist as a key in redis

            tries = 0
            link_key = None
            while tries < 6:
                link_key = self._set_unique_keyed_record(
                    json.dumps(new_link_json)
                )
                if link_key:
                    break
                tries += 1

            # If link key successfully saved then return
            if link_key:
                magic_link = (
                    env.config.get("AUTHENTICATOR_HOST")
                    + "/magic-links/"
                    + link_key
                )
                new_link_json.update(
                    {
                        "key": link_key,
                        "link": magic_link,
                    }
                )
                return magic_link_201_response(new_link_json)
            return error_response(500, "Could not create a unique link")
        return error_response(401, "Account does not exist")
