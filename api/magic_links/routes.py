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
        from app import redis_mlinks

        return redis_mlinks

    @property
    def _links(self):
        links = [link.decode("utf-8") for link in self.redis_mlinks.keys("*")]
        return links

    @staticmethod
    def _make_short_key():
        letters = string.ascii_letters
        return "".join(random.choice(letters) for i in range(8))

    @staticmethod
    def _make_link_json(account: Account, redirect_url: str):
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
        key = self._make_short_key()
        created = self.redis_mlinks.setex(
            key, env.config.get("MAGIC_LINK_EXPIRY_SECONDS", 0), value
        )
        if created == 1:
            return key

    def search(self):
        return Response(json.dumps(self._links), mimetype="application/json")

    def use(self, link_id: str):
        link_hash = self.redis_mlinks.get(link_id)
        if link_hash:
            link = json.loads(link_hash)
            self.redis_mlinks.delete(link_id)
            if link.get("exp") > int(datetime.now().timestamp()):
                return AuthSessionView.create_session_and_redirect(
                    account_id=link.get("accountId"),
                    redirect_url=link.get("redirectUrl"),
                )
            return error_response(404, "Link expired")
        return error_response(404, "Link expired or invalid")

    def create(self, email: str, redirect_url: str = "https://google.com"):
        account = get_account(email)
        if account:
            new_link_json = self._make_link_json(account, redirect_url)
            tries = 0
            link_key = None
            while tries < 6:
                link_key = self._set_unique_keyed_record(
                    json.dumps(new_link_json)
                )
                if link_key:
                    break
                tries += 1
            if link_key:
                new_link_json.update(
                    {
                        "key": link_key,
                        "link": env.config.get("AUTHENTICATOR_HOST")
                        + "/magic-links/"
                        + link_key,
                    }
                )
                return magic_link_201_response(new_link_json)
            return error_response(500, "Could not create a unique link")
        return error_response(401, "Account does not exist")
