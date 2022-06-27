"""Flask Test Environment Configuration."""
import base64
from os import environ

import redis
from config.environments.default import DefaultConfig as Config
from config.utils import VcapServices
from fsd_utils import configclass


@configclass
class TestConfig(Config):

    SECRET_KEY = environ.get("SECRET_KEY", "test")

    # GOV.UK PaaS
    VCAP_SERVICES = VcapServices.from_env_json(environ.get("VCAP_SERVICES"))

    # Redis
    REDIS_INSTANCE_NAME = "funding-service-magic-links-test"
    REDIS_INSTANCE_URI = VCAP_SERVICES.get_service_credentials_value(
        "redis", REDIS_INSTANCE_NAME, "uri"
    )
    REDIS_MLINKS_URL = REDIS_INSTANCE_URI + "/0"
    REDIS_SESSIONS_URL = REDIS_INSTANCE_URI + "/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)
    RSA256_PRIVATE_KEY = base64.b64decode(
        environ.get("RSA256_PRIVATE_KEY_BASE64")
    ).decode()
    RSA256_PUBLIC_KEY = base64.b64decode(
        environ.get("RSA256_PUBLIC_KEY_BASE64")
    ).decode()
