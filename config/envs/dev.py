"""Flask Dev Pipeline Environment Configuration."""
import logging
from os import environ

import redis
from config.envs.default import DefaultConfig as Config
from config.utils import VcapServices
from fsd_utils import configclass


@configclass
class DevConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"

    COOKIE_DOMAIN = environ.get("COOKIE_DOMAIN", ".dev.fundingservice.co.uk")

    # Logging
    FSD_LOG_LEVEL = logging.INFO

    # Azure Active Directory Config
    # This secret is only used for testing purposes
    AZURE_AD_CLIENT_ID = (
        # Application (client) ID of app registration on Azure AD
        environ.get("AZURE_AD_CLIENT_ID", "d8be82a8-541c-4768-9296-84bd779a24d9")
    )
    AZURE_AD_CLIENT_SECRET = environ.get(
        "AZURE_AD_CLIENT_SECRET",
        "nmq8Q~acUEOPWmjfvbOEQLPZy2M38yLe1PEh_cS2"
    )
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
    AZURE_AD_REDIRECT_URI = Config.AUTHENTICATOR_HOST + AZURE_AD_REDIRECT_PATH

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
