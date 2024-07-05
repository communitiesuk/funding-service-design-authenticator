"""Flask Production Environment Configuration."""
from os import getenv

from config.envs.default import DefaultConfig as Config
from distutils.util import strtobool
from fsd_utils import configclass


@configclass
class ProductionConfig(Config):
    # Session
    ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK = strtobool(getenv("ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK", "False"))
