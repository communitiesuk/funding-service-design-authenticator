import json
import logging

import msal
import requests
from config import Config


# Optional logging
# logging.basicConfig(level=logging.DEBUG)  # Enable DEBUG log for entire script
# logging.getLogger("msal").setLevel(logging.INFO)  # Optionally disable MSAL DEBUG logs


# Create a preferably long-lived app instance which maintains a token cache.
SCOPES = ["User.ReadBasic.All"]
ENDPOINT = "https://graph.microsoft.com/v1.0/users"
app = msal.ClientApplication(
    client_id=Config.AZURE_AD_CLIENT_ID,
    authority=Config.AZURE_AD_AUTHORITY,
    client_credential=Config.AZURE_AD_CLIENT_SECRET,
    # token_cache=...  # Default cache is in memory only.
    # You can learn how to use SerializableTokenCache from
    # https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
)

# The pattern to acquire a token looks like this.
result = None

# Firstly, check the cache to see if this end user has signed in before
accounts = app.get_accounts(username=Config.AZURE_AD_CLIENT_USERNAME)
if accounts:
    logging.info("Account(s) exists in cache, probably with token too. Let's try.")
    result = app.acquire_token_silent(["User.ReadBasic.All"], account=accounts[0])

if not result:
    logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
    # See this page for constraints of Username Password Flow.
    # https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication
    result = app.acquire_token_by_username_password(
        Config.AZURE_AD_CLIENT_USERNAME, Config.AZURE_AD_CLIENT_PASSWORD, scopes=SCOPES
    )

if "x" in result:
    # Calling graph using the access token
    graph_data = requests.get(  # Use token to call downstream service
        ENDPOINT,
        headers={"Authorization": "Bearer " + result["access_token"]},
    ).json()
    print("Graph API call result: %s" % json.dumps(graph_data, indent=2))
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug
    if 65001 in result.get("error_codes", []):  # Not mean to be coded programatically, but...
        # AAD requires user consent for U/P flow
        print("Visit this to consent:", app.get_authorization_request_url(SCOPES))
