"""Flask configuration."""
import base64
import logging
from os import environ
from os import getenv
from pathlib import Path

from config.utils import VcapServices
from distutils.util import strtobool
from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class DefaultConfig(object):
    #  Application Config
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")

    COOKIE_DOMAIN = environ.get("COOKIE_DOMAIN", None)

    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = environ.get("FLASK_ENV")
    SUPPORT_MAILBOX_EMAIL = "fsd.support@levellingup.gov.uk"

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
    SSO_LOGOUT_ENDPOINT = "/sso/logout"
    SSO_LOGIN_ENDPOINT = "/sso/login"
    SSO_POST_SIGN_OUT_URL = (
        AUTHENTICATOR_HOST + "/service/sso/signed-out/signout-request"
    )

    """
    Azure Configuration
    """
    # Azure Active Directory Config
    AZURE_AD_CLIENT_ID = (
        # Application (client) ID of app registration on Azure AD
        environ.get("AZURE_AD_CLIENT_ID")
    )
    AZURE_AD_CLIENT_SECRET = environ.get("AZURE_AD_CLIENT_SECRET")
    AZURE_AD_TENANT_ID = environ.get("AZURE_AD_TENANT_ID", "")
    AZURE_AD_AUTHORITY = (
        # consumers|organizations|<tenant_id> - signifies the Azure AD tenant endpoint # noqa
        "https://login.microsoftonline.com/"
        + AZURE_AD_TENANT_ID
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

    # GOV.UK PaaS
    if environ.get("VCAP_SERVICES"):
        VCAP_SERVICES = VcapServices.from_env_json(
            environ.get("VCAP_SERVICES")
        )

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
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    # Funding Service Design
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    FSD_SESSION_TIMEOUT_SECONDS = CommonConfig.FSD_SESSION_TIMEOUT_SECONDS
    WTF_CSRF_TIME_LIMIT = CommonConfig.WTF_CSRF_TIME_LIMIT
    CREATE_APPLICATION_ON_ACCOUNT_CREATION = False

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
    APPLICANT_FRONTEND_CONTACT_US_URL = APPLICANT_FRONTEND_HOST + "/contact_us"
    APPLICATION_ALL_QUESTIONS_URL = (
        APPLICANT_FRONTEND_HOST + "/cof_r2w2_all_questions"
    )

    # Assessment Frontend
    ASSESSMENT_FRONTEND_HOST = environ.get("ASSESSMENT_FRONTEND_HOST", "")
    ASSESSMENT_POST_LOGIN_URL = ASSESSMENT_FRONTEND_HOST
    FSD_ASSESSMENT_SESSION_TIMEOUT_SECONDS = (
        CommonConfig.FSD_SESSION_TIMEOUT_SECONDS
    )

    # Fund store service
    FUND_STORE_API_HOST = CommonConfig.FUND_STORE_API_HOST
    FUND_STORE_FUND_ENDPOINT = CommonConfig.FUND_ENDPOINT

    GET_ROUND_DATA_FOR_FUND_ENDPOINT = (
        FUND_STORE_API_HOST + CommonConfig.ROUND_ENDPOINT
    )

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

    USE_LOCAL_DATA = strtobool(getenv("USE_LOCAL_DATA", "False"))

    # Secure (Default) Content Security Policy (for Talisman Config)
    SECURE_CSP = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
        ],
        "connect-src": "",  # APPLICATION_STORE_API_HOST_PUBLIC,
        "img-src": ["data:", "'self'"],
    }

    # Swagger Content Security Policy (less secure)
    # - Allow inline scripts for swagger docs (for Talisman Config)
    SWAGGER_CSP = {
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
    }

    # Talisman Config
    FSD_REFERRER_POLICY = "strict-origin-when-cross-origin"
    FSD_USER_TOKEN_COOKIE_SAMESITE = "Strict"
    FSD_PERMISSIONS_POLICY = {"interest-cohort": "()"}
    FSD_DOCUMENT_POLICY = {}
    FSD_FEATURE_POLICY = {
        "microphone": "'none'",
        "camera": "'none'",
        "geolocation": "'none'",
    }

    DENY = "DENY"
    SAMEORIGIN = "SAMEORIGIN"
    ALLOW_FROM = "ALLOW-FROM"
    ONE_YEAR_IN_SECS = 31556926

    FORCE_HTTPS = True

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
        "session_cookie_samesite": SESSION_COOKIE_SAMESITE,
        "x_content_type_options": True,
        "x_xss_protection": True,
    }

    COF_FUND_ID = "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4"
    COF_ROUND2_ID = "c603d114-5364-4474-a0c4-c41cbf4d3bbd"
    DEFAULT_FUND_ID = COF_FUND_ID
    DEFAULT_ROUND_ID = COF_ROUND2_ID
    BABEL_TRANSLATION_DIRECTORIES = "frontend/translations"
