"""Flask configuration."""
import logging
from os import environ
from pathlib import Path

from fsd_utils import configclass


@configclass
class DefaultConfig(object):
    #  Application Config
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")
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
    FSD_SESSION_TIMEOUT_SECS = 3600  # 1 hour

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

    # Applicant Frontend
    APPLICANT_FRONTEND_HOST = environ.get("APPLICANT_FRONTEND_HOST")

    """
    Magic Links
    """
    MAGIC_LINK_EXPIRY_DAYS = 1
    MAGIC_LINK_EXPIRY_SECONDS = 86400 * MAGIC_LINK_EXPIRY_DAYS
    MAGIC_LINK_REDIRECT_HOST = APPLICANT_FRONTEND_HOST
    MAGIC_LINK_REDIRECT_URL = environ.get("MAGIC_LINK_REDIRECT_URL")
    if not MAGIC_LINK_REDIRECT_URL:
        if MAGIC_LINK_REDIRECT_HOST:
            MAGIC_LINK_REDIRECT_URL = (
                MAGIC_LINK_REDIRECT_HOST + "/account/{account_id}"
            )
        else:
            MAGIC_LINK_REDIRECT_URL = "https://www.gov.uk/error"
    MAGIC_LINK_RECORD_PREFIX = "link"
    MAGIC_LINK_USER_PREFIX = "account"
    MAGIC_LINK_LANDING_PAGE = "/magic-links/landing/"

    """
    Security
    """
    # RSA 256 KEYS
    RSA256_PRIVATE_KEY = environ.get("RSA256_PRIVATE_KEY")
    RSA256_PUBLIC_KEY = environ.get("RSA256_PUBLIC_KEY")

    # Talisman Config
    FORCE_HTTPS = True

    # Content Security Policy
    SECURE_CSP = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
        ],
        "img-src": ["data:", "'self'"],
    }

    # Content Security Policy for Swagger (Allow inline scripts)
    SWAGGER_CSP = {
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
    }

    # Security headers and other policies
    FSD_REFERRER_POLICY = "strict-origin-when-cross-origin"
    FSD_SESSION_COOKIE_SAMESITE = "Lax"
    FSD_PERMISSIONS_POLICY = {"interest-cohort": "()"}
    FSD_DOCUMENT_POLICY = {}
    FSD_FEATURE_POLICY = {
        "microphone": "'bob'",
        "camera": "'none'",
        "geolocation": "'none'",
    }

    DENY = "DENY"
    SAMEORIGIN = "SAMEORIGIN"
    ALLOW_FROM = "ALLOW-FROM"
    ONE_YEAR_IN_SECS = 31556926

    TALISMAN_SETTINGS = {
        "feature_policy": FSD_FEATURE_POLICY,
        "permissions_policy": FSD_PERMISSIONS_POLICY,
        "document_policy": FSD_DOCUMENT_POLICY,
        "force_https": FORCE_HTTPS,
        "force_https_permanent": False,
        "force_file_save": False,
        "frame_options": "SAMEORIGIN",
        "frame_options_allow_from": None,
        "strict_transport_security": True,
        "strict_transport_security_preload": True,
        "strict_transport_security_max_age": ONE_YEAR_IN_SECS,
        "strict_transport_security_include_subdomains": True,
        "content_security_policy": SECURE_CSP,
        "content_security_policy_report_uri": None,
        "content_security_policy_report_only": False,
        "content_security_policy_nonce_in": None,
        "referrer_policy": FSD_REFERRER_POLICY,
        "session_cookie_secure": True,
        "session_cookie_http_only": True,
        "session_cookie_samesite": FSD_SESSION_COOKIE_SAMESITE,
        "x_content_type_options": True,
        "x_xss_protection": True,
    }

    # # Security Settings (for Talisman Config)
    # FORCE_HTTPS = True
    #
    # # Content Security Policy (for Talisman Config)
    # SECURE_CSP = {
    #     "default-src": "'self'",
    #     "script-src": [
    #         "'self'",
    #         "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
    #         "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
    #     ],
    #     "img-src": ["data:", "'self'"],
    # }
    #
    # # Allow inline scripts for swagger docs (for Talisman Config)
    # SWAGGER_CSP = {
    #     "script-src": ["'self'", "'unsafe-inline'"],
    #     "style-src": ["'self'", "'unsafe-inline'"],
    # }
    #
    # # HTTP Strict-Transport-Security (for Talisman Config)
    # HSTS_HEADERS = {
    #     "strict-transport-security": (
    #         "max-age=31536000; includeSubDomains; preload"
    #     ),
    #     "X-Content-Type-Options": "nosniff",
    #     "X-Frame-Options": "SAMEORIGIN",
    #     "X-XSS-Protection": "1; mode=block",
    #     "Feature_Policy": (
    #         "microphone 'none'; camera 'none'; geolocation 'none'"
    #     ),
    # }
