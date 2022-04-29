"""Flask configuration."""
from os import environ
from os import path


class Config(object):
    #  Application Config
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME")
    FLASK_ROOT = path.dirname(path.dirname(path.realpath(__file__)))
    FLASK_ENV = environ.get("FLASK_ENV")

    #  Azure Active Directory Config
    CLIENT_ID = (  # Application (client) ID of app registration on Azure AD
        "d8be82a8-541c-4768-9296-84bd779a24d9"
    )

    CLIENT_SECRET = environ.get("CLIENT_SECRET")

    AUTHORITY = (  # consumers|organisations
        "https://login.microsoftonline.com/consumers"
    )
    # AUTHORITY signifies the Active Directory tenant endpoint

    REDIRECT_PATH = (  # Used for forming an absolute URL to your redirect URI.
        "/auth/msal/get-token"
    )
    # The absolute URL must match the redirect URI you set
    # in the app's registration in the Azure portal.

    AUTHENTICATOR_HOST = environ.get("AUTHENTICATOR_HOST", "")
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

    # RSA 256 KEYS
    RSA256_PRIVATE_KEY = environ.get("RSA256_PRIVATE_KEY")
    RSA256_PUBLIC_KEY = environ.get("RSA256_PUBLIC_KEY")

    # Redis
    REDIS_URL = "redis://:password@localhost:6379/0"
