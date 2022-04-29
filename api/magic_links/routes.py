import json
import random
import string
from datetime import datetime
from datetime import timedelta

import jwt
from config.env import env
from flask import abort
from flask import make_response
from flask import redirect
from flask import Response
from flask.views import MethodView


class MagicLinksView(MethodView):

    accounts = {
        "h@a.com": {"id": "h"},
        "a@a.com": {"id": "a"},
    }

    @property
    def redis_client(self):
        from app import redis_client

        return redis_client

    @property
    def links(self):
        if len(self.redis_client.keys("*")) == 0:
            inital_link = {
                "token": "123",
                "accountId": "h",
                "expiry": "EPOCH",
                "redirectUrl": "https://google.com",
            }
            self.redis_client.set("a", json.dumps(inital_link))
        links = [link.decode("utf-8") for link in self.redis_client.keys("*")]
        return links

    def search(self):
        return Response(json.dumps(self.links), mimetype="application/json")

    def use(self, link_id: str):
        link_hash = self.redis_client.get(link_id)
        if link_hash:
            link = json.loads(link_hash)
            redirect_url = link.get("redirectUrl")
            self.redis_client.delete(link_id)
            return redirect(redirect_url), 302
        abort(404, "Link expired or invalid")

    def create(self, email: str):
        account = self.accounts.get(email)
        if account:
            new_link_json = {
                "accountId": account["id"],
                "expiry": datetime.isoformat(
                    datetime.now() + timedelta(days=1)
                ),
                "redirectUrl": "https://google.com",
            }
            new_link_json.update({"token": self._create_token(new_link_json)})
            letters = string.ascii_letters
            nice_link = "".join(random.choice(letters) for i in range(8))
            self.redis_client.set(nice_link, json.dumps(new_link_json))
            return make_response(new_link_json), 200
        abort(401, "Account does not exist")

    @staticmethod
    def _create_token(link_json):
        return jwt.encode(
            link_json, env.config.get("RSA256_PRIVATE_KEY"), algorithm="RS256"
        )
