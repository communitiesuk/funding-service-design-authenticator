"""Flask Development Environment Configuration."""
from os import path

import redis
from config.default import Config


class DevelopmentConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"
    SESSION_COOKIE_NAME = "session_cookie"
    FLASK_ROOT = path.dirname(path.dirname(path.realpath(__file__)))
    FLASK_ENV = "development"

    CLIENT_SECRET = "nmq8Q~acUEOPWmjfvbOEQLPZy2M38yLe1PEh_cS2"

    AUTHORITY = (  # consumers|organisations
        "https://login.microsoftonline.com/consumers"
    )
    # AUTHORITY signifies the Active Directory tenant endpoint

    REDIRECT_PATH = (  # Used for forming an absolute URL to your redirect URI.
        "/sso/get-token"
    )
    # The absolute URL must match the redirect URI you set
    # in the app's registration in the Azure portal.

    AUTHENTICATOR_HOST = "http://localhost:5000"
    REDIRECT_URI = AUTHENTICATOR_HOST + REDIRECT_PATH

    SESSION_TYPE = (
        # Specifies how the token cache should be stored
        # in server-side session
        # "filesystem"
        "redis"
    )
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    # RSA 256 KEYS
    _test_private_key_path = FLASK_ROOT + "/tests/keys/rsa256/private.pem"
    with open(_test_private_key_path, mode="rb") as private_key_file:
        RSA256_PRIVATE_KEY = private_key_file.read()
    _test_public_key_path = FLASK_ROOT + "/tests/keys/rsa256/public.pem"
    with open(_test_public_key_path, mode="rb") as public_key_file:
        RSA256_PUBLIC_KEY = public_key_file.read()

    # Redis
    REDIS_MLINKS_URL = "redis://localhost:6379/0"
    REDIS_SESSIONS_URL = "redis://localhost:6379/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)

    # APIs
    ACCOUNT_STORE_API_HOST = "account_store"

    # Security
    FORCE_HTTPS = False
