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
from flask import redirect
from flask import request
from flask import Response
from flask import url_for
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
    def _make_short_key(prefix=None) -> tuple:
        """
        Creates a short string to act as the magic link key
        :return: Random string
        """
        letters = string.ascii_letters
        short_key = "".join(random.choice(letters) for i in range(8))
        if prefix and prefix[-1] != ":":
            prefix = prefix + ":"
        return prefix + short_key, short_key

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

    def _set_unique_keyed_record(
        self, value: str, prefix=None, max_tries: int = 6
    ) -> tuple | None:
        """
        Attempts up to max_tries to save the record with a unique short key
        that doesn't already exist (and returns None if it fails)
        :param value: A string value
        :param prefix: A string key prefix
        :param max_tries: An integer of the maximum tries
        :return: The unique short key for the link hash (or None)
        """
        for _ in range(max_tries):
            prefixed_key, unique_key = self._make_short_key(prefix)
            created = self.redis_mlinks.setex(
                prefixed_key,
                env.config.get("MAGIC_LINK_EXPIRY_SECONDS", 0),
                value,
            )
            if created:
                return prefixed_key, unique_key

    def _create_user_record(self, account: Account, link_redis_key: str):
        """
        Creates a record with a key of {MAGIC_LINK_USER_PREFIX}:{account.id}
        with a value of the created magic link redis record key,
        to act as a reference of the link record against the account id
        for management processes, to ensure that only one link can exist
        for a user at any one time
        :param account: Account instance of user
        :param link_redis_key: String of the currently active key
        :return: 1 if successfully created, or 0 if not
        """
        prefixed_user_key = ":".join(
            [
                env.config.get("MAGIC_LINK_USER_PREFIX"),
                account.id,
            ]
        )
        created = self.redis_mlinks.setex(
            prefixed_user_key,
            env.config.get("MAGIC_LINK_EXPIRY_SECONDS", 0),
            link_redis_key,
        )
        return created

    def _clear_existing_user_link(self, account: Account):
        """
        Checks to see if the account has an existing active magic link
        and deletes it if so
        :param account: Account instance of the user
        :return: True if existing link is cleared
        """
        user_record_key = ":".join(
            [env.config.get("MAGIC_LINK_USER_PREFIX"), account.id]
        )
        existing_link_key = self.redis_mlinks.get(user_record_key)
        if existing_link_key:
            self.redis_mlinks.delete(existing_link_key)
            return True

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
        - deletes the user record from redis
        - then finally, redirects to the redirect_url
        If no matching valid link is found returns a 404 error message
        :param link_id: String short key for the link
        :return: 302 Redirect / 404 Error
        """
        link_key = ":".join(
            [env.config.get("MAGIC_LINK_RECORD_PREFIX"), link_id]
        )
        link_hash = self.redis_mlinks.get(link_key)
        if link_hash:
            link = json.loads(link_hash)
            user_key = ":".join(
                [
                    env.config.get("MAGIC_LINK_USER_PREFIX"),
                    link.get("accountId"),
                ]
            )
            self.redis_mlinks.delete(link_key)
            self.redis_mlinks.delete(user_key)

            # Check link is not expired
            if link.get("exp") > int(datetime.now().timestamp()):
                return AuthSessionView.create_session_and_redirect(
                    account_id=link.get("accountId"),
                    redirect_url=link.get("redirectUrl"),
                )
            return redirect(
                url_for("magic_links_bp.invalid", error="Link expired")
            )
        return redirect(
            url_for("magic_links_bp.invalid", error="Link expired or invalid")
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
        if not redirect_url:
            redirect_url = env.config.get("MAGIC_LINK_REDIRECT_URL")
        account = get_account(email)
        if account:
            self._clear_existing_user_link(account)
            new_link_json = self._make_link_json(account, redirect_url)

            redis_key, link_key = self._set_unique_keyed_record(
                json.dumps(new_link_json),
                env.config.get("MAGIC_LINK_RECORD_PREFIX"),
            )

            # If link key successfully saved, create user record then return
            if link_key:
                self._create_user_record(account, redis_key)

                magic_link_url = (
                    env.config.get("AUTHENTICATOR_HOST")
                    + "/magic-links/"
                    + link_key
                )
                new_link_json.update(
                    {
                        "key": link_key,
                        "link": magic_link_url,
                    }
                )
                return magic_link_201_response(new_link_json)
            return error_response(500, "Could not create a unique link")
        return error_response(401, "Account does not exist")
