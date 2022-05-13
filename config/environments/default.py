"""Flask configuration."""
from os import environ
from os import path


class Config(object):
    #  Application Config
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME")
    FLASK_ROOT = path.dirname(
        path.dirname(path.dirname(path.realpath(__file__)))
    )
    FLASK_ENV = environ.get("FLASK_ENV")

    # Frontend
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True

    # Hostname for this service
    AUTHENTICATOR_HOST = environ.get("AUTHENTICATOR_HOST", "")

    # Azure Active Directory Config
    AZURE_AD_CLIENT_ID = (
        # Application (client) ID of app registration on Azure AD
        "d8be82a8-541c-4768-9296-84bd779a24d9"
    )
    AZURE_AD_CLIENT_SECRET = environ.get("AZURE_AD_CLIENT_SECRET")
    AZURE_AD_AUTHORITY = (
        # consumers|organisations - signifies the Azure AD tenant endpoint
        "https://login.microsoftonline.com/consumers"
    )
    AZURE_AD_REDIRECT_PATH = (
        # Used for forming an absolute URL to your redirect URI.
        "/sso/get-token"
    )
    # The absolute URL must match the redirect URI you set
    # in the app's registration in the Azure portal.
    AZURE_AD_REDIRECT_URI = AUTHENTICATOR_HOST + AZURE_AD_REDIRECT_PATH

    # You can find more Microsoft Graph API endpoints from Graph Explorer
    # https://developer.microsoft.com/en-us/graph/graph-explorer
    MS_GRAPH_ENDPOINT = (  # This resource requires no admin consent
        "https://graph.microsoft.com/v1.0/users"
    )

    # You can find the proper permission names from this document
    # https://docs.microsoft.com/en-us/graph/permissions-reference
    MS_GRAPH_PERMISSIONS_SCOPE = ["User.ReadBasic.All"]

    SESSION_TYPE = (
        # Specifies how the token cache should be stored
        # in server-side session
        # "filesystem"
        "redis"
    )
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    # RSA 256 KEYS
    RSA256_PRIVATE_KEY = environ.get("RSA256_PRIVATE_KEY")
    RSA256_PUBLIC_KEY = environ.get("RSA256_PUBLIC_KEY")

    # Funding Service Design
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    FSD_SESSION_TIMEOUT_SECS = 3600  # 1 hour
    MAGIC_LINK_EXPIRY_DAYS = 0
    MAGIC_LINK_EXPIRY_MINUTES = 1
    MAGIC_LINK_EXPIRY_SECONDS = (86400 * MAGIC_LINK_EXPIRY_DAYS) + (
        60 * MAGIC_LINK_EXPIRY_MINUTES
    )
    MAGIC_LINK_REDIRECT_URL = "https://example.com"
    MAGIC_LINK_RECORD_PREFIX = "link"
    MAGIC_LINK_USER_PREFIX = "account"
    NEW_MAGIC_LINK_URL = "/service/magic-links"

    # APIs
    ACCOUNT_STORE_API_HOST = environ.get("ACCOUNT_STORE_API_HOST")
    # Account Store Endpoints
    ACCOUNT_STORE_ACCOUNT_ENDPOINT = "/accounts?email_address={email}"

    # Security Settings (for Talisman Config)
    FORCE_HTTPS = True

    # Content Security Policy (for Talisman Config)
    SECURE_CSP = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
        ],
        "img-src": ["data:", "'self'"],
    }

    # Allow inline scripts for swagger docs (for Talisman Config)
    SWAGGER_CSP = {
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
    }

    # HTTP Strict-Transport-Security (for Talisman Config)
    HSTS_HEADERS = {
        "Strict-Transport-Security": (
            "max-age=31536000; includeSubDomains; preload"
        ),
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Feature_Policy": (
            "microphone 'none'; camera 'none'; geolocation 'none'"
        ),
    }
