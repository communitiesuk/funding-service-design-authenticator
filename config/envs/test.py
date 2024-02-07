"""Flask Test Environment Configuration."""
import base64
from os import environ
from os import getenv

import redis
from config.envs.default import DefaultConfig as Config
from distutils.util import strtobool
from fsd_utils import configclass


@configclass
class TestConfig(Config):

    SECRET_KEY = environ.get("SECRET_KEY", "test")

    COOKIE_DOMAIN = environ.get("COOKIE_DOMAIN", ".test.fundingservice.co.uk")

    # Redis
    REDIS_INSTANCE_NAME = "funding-service-magic-links-test"

    if not hasattr(Config, "VCAP_SERVICES"):
        REDIS_INSTANCE_URI = getenv("REDIS_INSTANCE_URI", "redis://localhost:6379")
    else:
        REDIS_INSTANCE_URI = Config.VCAP_SERVICES.get_service_credentials_value("redis", REDIS_INSTANCE_NAME, "uri")

    REDIS_MLINKS_URL = REDIS_INSTANCE_URI + "/0"
    REDIS_SESSIONS_URL = REDIS_INSTANCE_URI + "/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)
    RSA256_PRIVATE_KEY = base64.b64decode(environ.get("RSA256_PRIVATE_KEY_BASE64")).decode()
    RSA256_PUBLIC_KEY = base64.b64decode(environ.get("RSA256_PUBLIC_KEY_BASE64")).decode()

    # Session
    ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK = strtobool(getenv("ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK", "True"))
