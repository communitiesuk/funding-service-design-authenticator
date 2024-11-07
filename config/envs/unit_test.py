"""Flask Local Development Environment Configuration."""
import logging
from os import environ
from os import getenv

import redis
from config.envs.default import DefaultConfig as Config
from config.envs.default import SafeAppConfig
from distutils.util import strtobool
from fsd_utils import configclass
from fsd_utils.authentication.config import SupportedApp


@configclass
class UnitTestConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"  # pragma: allowlist secret
    COOKIE_DOMAIN = None

    # Logging
    FSD_LOG_LEVEL = logging.DEBUG

    # Hostname for this service
    AUTHENTICATOR_HOST = environ.get("AUTHENTICATOR_HOST", "https://example.com")

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

    SESSION_TYPE = (
        # Specifies how the token cache should be stored
        # in server-side session
        # "filesystem"
        "redis"
    )
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False
    ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK = strtobool(getenv("ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK", "False"))

    # RSA 256 KEYS
    _test_private_key_path = Config.FLASK_ROOT + "/tests/keys/rsa256/private.pem"
    with open(_test_private_key_path, mode="rb") as private_key_file:
        RSA256_PRIVATE_KEY = private_key_file.read()
    _test_public_key_path = Config.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
    with open(_test_public_key_path, mode="rb") as public_key_file:
        RSA256_PUBLIC_KEY = public_key_file.read()

    # Redis
    REDIS_MLINKS_URL = "redis://localhost:6379/0"
    REDIS_SESSIONS_URL = "redis://localhost:6379/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)
    ACCOUNT_STORE_API_HOST = "account_store"

    # Security
    Config.TALISMAN_SETTINGS["force_https"] = False
    WTF_CSRF_ENABLED = False

    # ---------------
    # S3 Config
    # ---------------
    AWS_MSG_BUCKET_NAME = "fsd-notification-bucket"

    POST_AWARD_FRONTEND_HOST = "http://post-award-frontend"

    SAFE_RETURN_APPS = {
        SupportedApp.POST_AWARD_FRONTEND.value: SafeAppConfig(
            login_url=POST_AWARD_FRONTEND_HOST + "/login",
            logout_endpoint="sso_bp.signed_out",
            service_title="Find monitoring and evaluation data",
        ),
        SupportedApp.POST_AWARD_SUBMIT.value: SafeAppConfig(
            login_url="http://submit/",
            logout_endpoint="sso_bp.signed_out",
            service_title="Submit monitoring and evaluation data",
        ),
    }
