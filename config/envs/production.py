"""Flask Production Environment Configuration."""
from os import getenv

import redis
from config.envs.default import DefaultConfig as Config
from distutils.util import strtobool
from fsd_utils import configclass


@configclass
class ProductionConfig(Config):

    # Redis
    REDIS_INSTANCE_URI = getenv("REDIS_INSTANCE_URI", "redis://localhost:6379")
    REDIS_MLINKS_URL = REDIS_INSTANCE_URI + "/0"
    REDIS_SESSIONS_URL = REDIS_INSTANCE_URI + "/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)

    # Session
    ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK = strtobool(getenv("ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK", "False"))
