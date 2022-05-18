import json
import os
import urllib.parse

import requests
from config.env import env


def api_call(endpoint: str, method: str = "GET", params: dict = None):
    cleaned_params = {k: v for k, v in params.items() if v is not None}
    if endpoint[:8] == "https://":
        req = requests.PreparedRequest()
        req.prepare_url(endpoint, cleaned_params)
        if method:
            if method == "POST":
                return requests.post(req.url)
            elif method == "GET":
                return requests.get(req.url)
    else:
        return local_api_call(endpoint, cleaned_params, method)


def get_data(endpoint: str, params: dict = None):
    cleaned_params = {k: v for k, v in params.items() if v is not None}
    if endpoint[:8] == "https://":
        req = requests.PreparedRequest()
        req.prepare_url(endpoint, cleaned_params)
        response = requests.get(req.url)
        if response.status_code == 200:
            return response.json()
    else:
        return local_api_call(endpoint, cleaned_params, "get")


def post_data(endpoint: str, params: dict = None):
    cleaned_params = {k: v for k, v in params.items() if v is not None}
    if endpoint[:8] == "https://":
        req = requests.PreparedRequest()
        req.prepare_url(endpoint, cleaned_params)
        response = requests.post(req.url)
        if response.status_code in [200, 201]:
            return response.json()
    else:
        return local_api_call(endpoint, cleaned_params, "post")


def local_api_call(endpoint: str, params: dict = None, method: str = "get"):
    api_data_json = os.path.join(
        env.config.get("FLASK_ROOT"),
        "tests",
        "api_data",
        method.lower() + "_endpoint_data.json",
    )
    fp = open(api_data_json)
    api_data = json.load(fp)
    fp.close()
    query_params = "_"
    if params:
        query_params = urllib.parse.urlencode(params)
    if method.lower() == "post":
        print(endpoint)
        if endpoint in api_data:
            post_dict = api_data.get(endpoint)
            print(query_params)
            if query_params in post_dict:
                return post_dict.get(query_params)
            else:
                return post_dict.get("_default")
    else:
        endpoint = f"{endpoint}?{query_params}"
        print(endpoint)
        if endpoint in api_data:
            return api_data.get(endpoint)
