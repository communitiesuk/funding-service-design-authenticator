"""Flask Dev Pipeline Environment Configuration."""
import logging
from os import environ
from os import path

import redis
from config.default import DefaultConfig as Config
from config.utils import VcapServices
from fsd_tech import configclass


@configclass
class DevConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"
    SESSION_COOKIE_NAME = "session_cookie"
    AUTHENTICATOR_HOST = environ.get("AUTHENTICATOR_HOST", "")
    FLASK_ROOT = path.dirname(
        path.dirname(path.dirname(path.realpath(__file__)))
    )

    # Logging
    FSD_LOG_LEVEL = logging.INFO

    # Azure Active Directory Config
    # This secret is only used for testing purposes
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

    # RSA 256 KEYS
    _test_private_key_path = FLASK_ROOT + "/tests/keys/rsa256/private.pem"
    with open(_test_private_key_path, mode="rb") as private_key_file:
        RSA256_PRIVATE_KEY = private_key_file.read()
    _test_public_key_path = FLASK_ROOT + "/tests/keys/rsa256/public.pem"
    with open(_test_public_key_path, mode="rb") as public_key_file:
        RSA256_PUBLIC_KEY = public_key_file.read()

    # GOV.UK PaaS
    VCAP_SERVICES = VcapServices.from_env_json(environ.get("VCAP_SERVICES"))

    # Redis
    REDIS_INSTANCE_NAME = "funding-service-magic-links-dev"
    REDIS_INSTANCE_URI = VCAP_SERVICES.get_service_credentials_value(
        "redis", REDIS_INSTANCE_NAME, "uri"
    )
    REDIS_MLINKS_URL = REDIS_INSTANCE_URI + "/0"
    REDIS_SESSIONS_URL = REDIS_INSTANCE_URI + "/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)
