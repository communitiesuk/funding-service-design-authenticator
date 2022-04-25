"""Flask configuration."""
from os import environ
from os import path

#  Application Config
SECRET_KEY = environ.get("SECRET_KEY") or "dev"
SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME") or "session_cookie"
FLASK_ROOT = path.dirname(path.realpath(__file__))
FLASK_ENV = environ.get("FLASK_ENV") or "development"

#  Azure Active Directory Config
CLIENT_ID = (  # Application (client) ID of app registration on Azure AD
    "d8be82a8-541c-4768-9296-84bd779a24d9"
)

if FLASK_ENV == "development":
    CLIENT_SECRET = (
        environ.get("CLIENT_SECRET")
        or "nmq8Q~acUEOPWmjfvbOEQLPZy2M38yLe1PEh_cS2"
    )
else:
    CLIENT_SECRET = environ.get("CLIENT_SECRET")
    if not CLIENT_SECRET:
        raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = (  # consumers|organisations
    "https://login.microsoftonline.com/consumers"
)
# AUTHORITY signifies the Active Directory tenant endpoint

REDIRECT_PATH = (  # Used for forming an absolute URL to your redirect URI.
    "/auth/msal/get-token"
)
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.

AUTHENTICATOR_HOST = (
    environ.get("AUTHENTICATOR_HOST") or "http://localhost:5000"
)
REDIRECT_URI = AUTHENTICATOR_HOST + REDIRECT_PATH

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = (  # This resource requires no admin consent
    "https://graph.microsoft.com/v1.0/users"
)

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = (
    # Specifies how the token cache should be stored
    # in server-side session
    "filesystem"
)
