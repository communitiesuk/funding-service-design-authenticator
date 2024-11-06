"""Flask Local Development Environment Configuration."""
import logging
from os import getenv

import redis
from config.envs.default import DefaultConfig as Config
from fsd_utils import configclass


@configclass
class DevelopmentConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"  # pragma: allowlist secret
    SESSION_COOKIE_NAME = "session_cookie"
    FLASK_ENV = "development"
    COOKIE_DOMAIN = getenv("COOKIE_DOMAIN", None)
    ASSETS_AUTO_BUILD = True
    # Logging
    FSD_LOG_LEVEL = logging.DEBUG

    # Hostname for this service
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "http://localhost:5000")

    # Azure Active Directory Config

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
        _test_private_key_path = Config.FLASK_ROOT + "/tests/keys/rsa256/private.pem"
        with open(_test_private_key_path, mode="rb") as private_key_file:
            RSA256_PRIVATE_KEY = private_key_file.read()
    if not hasattr(Config, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = Config.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    # Redis

    REDIS_INSTANCE_URI = getenv("REDIS_INSTANCE_URI", "redis://localhost:6379")
    REDIS_MLINKS_URL = f"{REDIS_INSTANCE_URI}/0"
    REDIS_SESSIONS_URL = f"{REDIS_INSTANCE_URI}/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)

    ACCOUNT_STORE_API_HOST = getenv("ACCOUNT_STORE_API_HOST", "account_store")

    AUTO_REDIRECT_LOGIN = True

    DISABLE_NOTIFICATION_SERVICE = False  # Toggle on if you have no notify api key.

    # Security
    Config.TALISMAN_SETTINGS["force_https"] = False

    # Connexion
    CONNEXION_OPTIONS = {
        "swagger_url": "/docs",
    }
