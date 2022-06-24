"""Flask Local Development Environment Configuration."""
import logging

import redis
from config.environments.default import DefaultConfig as Config
from fsd_utils import configclass


@configclass
class DevelopmentConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"
    SESSION_COOKIE_NAME = "session_cookie"
    FLASK_ENV = "development"

    # Logging
    FSD_LOG_LEVEL = logging.DEBUG

    # Hostname for this service
    AUTHENTICATOR_HOST = "http://localhost:5000"

    # Azure Active Directory Config
    # This secret is only used for local testing purposes
    AZURE_AD_CLIENT_SECRET = "nmq8Q~acUEOPWmjfvbOEQLPZy2M38yLe1PEh_cS2"
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

    SESSION_TYPE = (
        # Specifies how the token cache should be stored
        # in server-side session
        # "filesystem"
        "redis"
    )
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

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
    FUND_STORE_API_HOST = "fund_store"
    ROUND_STORE_API_HOST = "round_store"
    NOTIFICATION_SERVICE_HOST = "notification_service"

    # Security
    FORCE_HTTPS = False
