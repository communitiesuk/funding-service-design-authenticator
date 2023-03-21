"""Flask Local Development Environment Configuration."""
import logging
from os import getenv

import redis
from config.envs.default import DefaultConfig as Config
from fsd_utils import configclass


@configclass
class DevelopmentConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"
    SESSION_COOKIE_NAME = "session_cookie"
    FLASK_ENV = "development"
    COOKIE_DOMAIN = None

    # Logging
    FSD_LOG_LEVEL = logging.DEBUG

    # Hostname for this service
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "http://localhost:5000")
    SSO_POST_SIGN_OUT_URL = (
        AUTHENTICATOR_HOST + "/service/sso/signed-out/signout-request"
    )

    # Azure Active Directory Config
    AZURE_AD_AUTHORITY = (
        # consumers|organizations|<tenant_id> - signifies the Azure AD tenant endpoint # noqa
        "https://login.microsoftonline.com/organizations"
    )

    # The absolute URL must match the redirect URI you set
    # in the app's registration in the Azure portal.
    AZURE_AD_REDIRECT_URI = AUTHENTICATOR_HOST + Config.AZURE_AD_REDIRECT_PATH

    # Session Settings
    SESSION_TYPE = (
        # Specifies how the token cache should be stored
        # in server-side session
        # "filesystem"
        "redis"
    )
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False

    # RSA 256 KEYS
    if not hasattr(Config, "RSA256_PRIVATE_KEY"):
        _test_private_key_path = (
            Config.FLASK_ROOT + "/tests/keys/rsa256/private.pem"
        )
        with open(_test_private_key_path, mode="rb") as private_key_file:
            RSA256_PRIVATE_KEY = private_key_file.read()
    if not hasattr(Config, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = (
            Config.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        )
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    # Redis

    REDIS_INSTANCE_URI = getenv("REDIS_INSTANCE_URI", "redis://localhost:6379")
    REDIS_MLINKS_URL = f"{REDIS_INSTANCE_URI}/0"
    REDIS_SESSIONS_URL = f"{REDIS_INSTANCE_URI}/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)

    # APIs
    APPLICATION_STORE_API_HOST = getenv(
        "APPLICATION_STORE_API_HOST", "application_store"
    )
    ACCOUNT_STORE_API_HOST = getenv("ACCOUNT_STORE_API_HOST", "account_store")
    NOTIFICATION_SERVICE_HOST = getenv(
        "NOTIFICATION_SERVICE_HOST", "notification_service"
    )

    # Security
    Config.TALISMAN_SETTINGS["force_https"] = False
