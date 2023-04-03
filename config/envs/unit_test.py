"""Flask Local Development Environment Configuration."""
import logging
from os import getenv

import redis
from config.envs.default import DefaultConfig as Config
from distutils.util import strtobool
from fsd_utils import configclass


@configclass
class UnitTestConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"
    COOKIE_DOMAIN = None

    # Logging
    FSD_LOG_LEVEL = logging.DEBUG

    # Hostname for this service
    AUTHENTICATOR_HOST = "http://localhost:5000"

    # Azure Active Directory Config
    AZURE_AD_CLIENT_ID = "abc"
    AZURE_AD_CLIENT_SECRET = "123"
    AZURE_AD_TENANT_ID = "organizations"
    AZURE_AD_AUTHORITY = (
        # consumers|organizations|<tenant_id>
        # - signifies the Azure AD tenant endpoint
        "https://login.microsoftonline.com/"
        + AZURE_AD_TENANT_ID
    )

    # The absolute URL must match the redirect URI you set
    # in the app's registration in the Azure portal.
    AZURE_AD_REDIRECT_URI = AUTHENTICATOR_HOST + Config.AZURE_AD_REDIRECT_PATH

    SESSION_TYPE = (
        # Specifies how the token cache should be stored
        # in server-side session
        # "filesystem"
        "redis"
    )
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False
    ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK = strtobool(
        getenv("ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK", "False")
    )

    # RSA 256 KEYS
    _test_private_key_path = (
        Config.FLASK_ROOT + "/tests/keys/rsa256/private.pem"
    )
    with open(_test_private_key_path, mode="rb") as private_key_file:
        RSA256_PRIVATE_KEY = private_key_file.read()
    _test_public_key_path = Config.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
    with open(_test_public_key_path, mode="rb") as public_key_file:
        RSA256_PUBLIC_KEY = public_key_file.read()

    # Redis
    REDIS_MLINKS_URL = "redis://localhost:6379/0"
    REDIS_SESSIONS_URL = "redis://localhost:6379/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)

    # APIs
    APPLICATION_STORE_API_HOST = "application_store"
    ACCOUNT_STORE_API_HOST = "account_store"
    NOTIFICATION_SERVICE_HOST = "notification_service"

    # Security
    Config.TALISMAN_SETTINGS["force_https"] = False
    WTF_CSRF_ENABLED = False

    APPLICANT_FRONTEND_HOST = "frontend"
    APPLICANT_FRONTEND_ACCESSIBILITY_STATEMENT_URL = "/accessibility_statement"
    APPLICANT_FRONTEND_COOKIE_POLICY_URL = "/cookie_policy"

    # Assessment Frontend
    ASSESSMENT_FRONTEND_HOST = ""
    ASSESSMENT_POST_LOGIN_URL = ""
