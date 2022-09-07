"""Flask configuration."""
import base64
import logging
from os import environ
from os import getenv
from pathlib import Path

from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class DefaultConfig(object):
    #  Application Config
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")
    COOKIE_DOMAIN = getenv("COOKIE_DOMAIN")
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = environ.get("FLASK_ENV")

    # Logging
    FSD_LOG_LEVEL = logging.WARNING

    # Frontend
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = True

    # Hostname for this service
    AUTHENTICATOR_HOST = environ.get("AUTHENTICATOR_HOST", "")
    NEW_LINK_ENDPOINT = "/service/magic-links/new"

    """
    Azure Configuration
    """
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

    """
    Session
    """
    SESSION_TYPE = (
        # Specifies how the token cache should be stored
        # in server-side session
        # "filesystem"
        "redis"
    )
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    # Funding Service Design
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    FSD_SESSION_TIMEOUT_SECS = 86400  # 1 day

    """
    APIs Config: contains api hosts (set in manifest.yml)
    """
    # Account Store
    ACCOUNT_STORE_API_HOST = environ.get("ACCOUNT_STORE_API_HOST")
    ACCOUNTS_ENDPOINT = "/accounts"
    ACCOUNT_ENDPOINT = "/accounts/{account_id}"

    # Application Store
    APPLICATION_STORE_API_HOST = environ.get("APPLICATION_STORE_API_HOST")
    APPLICATIONS_ENDPOINT = "/applications"
    APPLICATION_ENDPOINT = "/applications/{account_id}"

    # Notification Service
    NOTIFICATION_SERVICE_HOST = environ.get("NOTIFICATION_SERVICE_HOST")
    SEND_ENDPOINT = "/send"
    NOTIFY_TEMPLATE_MAGIC_LINK = "MAGIC_LINK"
    NOTIFICATION_MAGIC_LINK_CONTACT_HELP_EMAIL = (
        CommonConfig.NOTIFICATION_MAGIC_LINK_CONTACT_HELP_EMAIL
    )
    NOTIFICATION_MAGIC_LINK_MAGIC_LINK_URL = (
        CommonConfig.NOTIFICATION_MAGIC_LINK_MAGIC_LINK_URL
    )
    NOTIFICATION_MAGIC_LINK_REQUEST_NEW_EMAIL_URL = (
        CommonConfig.NOTIFICATION_MAGIC_LINK_REQUEST_NEW_EMAIL_URL
    )
    NOTIFICATION_MAGIC_LINK_FUND_NAME = (
        CommonConfig.NOTIFICATION_MAGIC_LINK_FUND_NAME
    )

    # Applicant Frontend
    APPLICANT_FRONTEND_HOST = environ.get(
        "APPLICANT_FRONTEND_HOST", "frontend"
    )
    APPLICANT_FRONTEND_ACCESSIBILITY_STATEMENT_URL = (
        APPLICANT_FRONTEND_HOST + "/accessibility_statement"
    )
    APPLICANT_FRONTEND_COOKIE_POLICY_URL = (
        APPLICANT_FRONTEND_HOST + "/cookie_policy"
    )

    # Fund store service
    FUND_STORE_API_HOST = CommonConfig.FUND_STORE_API_HOST
    FUND_STORE_FUND_ENDPOINT = CommonConfig.FUND_ENDPOINT

    """
    Magic Links
    """
    MAGIC_LINK_EXPIRY_DAYS = 1
    MAGIC_LINK_EXPIRY_SECONDS = 86400 * MAGIC_LINK_EXPIRY_DAYS
    if APPLICANT_FRONTEND_HOST:
        MAGIC_LINK_REDIRECT_URL = APPLICANT_FRONTEND_HOST + "/account"
    else:
        MAGIC_LINK_REDIRECT_URL = "https://www.gov.uk/error"
    MAGIC_LINK_RECORD_PREFIX = "link"
    MAGIC_LINK_USER_PREFIX = "account"
    MAGIC_LINK_LANDING_PAGE = "/service/magic-links/landing/"
    FUND_ID_COF = "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4"

    """
    Security
    """
    # RSA 256 KEYS
    RSA256_PRIVATE_KEY_BASE64 = environ.get("RSA256_PRIVATE_KEY_BASE64")
    if RSA256_PRIVATE_KEY_BASE64:
        RSA256_PRIVATE_KEY = base64.b64decode(
            RSA256_PRIVATE_KEY_BASE64
        ).decode()
    RSA256_PUBLIC_KEY_BASE64 = environ.get("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

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
        "strict-transport-security": (
            "max-age=31536000; includeSubDomains; preload"
        ),
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Feature_Policy": (
            "microphone 'none'; camera 'none'; geolocation 'none'"
        ),
    }
