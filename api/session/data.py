import json
import os

import requests
from api.session.models.account import Account
from config.env import env


# Account Store Endpoints
ACCOUNTS_ENDPOINT = "/accounts/"
ACCOUNT_ENDPOINT = "/accounts/{email}"


def get_data(endpoint: str):
    if endpoint[:8] == "https://":
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
        else:
            return None
    else:
        data = get_local_data(endpoint)
    return data


def get_local_data(endpoint: str):
    print(endpoint)
    api_data_json = os.path.join(
        env.config.get("FLASK_ROOT"), "tests", "api_data", "endpoint_data.json"
    )
    fp = open(api_data_json)
    api_data = json.load(fp)
    fp.close()
    if endpoint in api_data:
        return api_data.get(endpoint)


def get_account(email: str) -> Account | None:
    endpoint = env.config.get(
        "ACCOUNT_STORE_API_HOST"
    ) + ACCOUNT_ENDPOINT.format(email=email)
    response = get_data(endpoint)
    if response and "id" in response:
        return Account.from_json(response)
    return None
