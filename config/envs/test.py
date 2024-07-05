"""Flask Test Environment Configuration."""
import base64
from os import environ
from os import getenv

from config.envs.default import DefaultConfig as Config
from distutils.util import strtobool
from fsd_utils import configclass


@configclass
class TestConfig(Config):

    SECRET_KEY = environ.get("SECRET_KEY", "test")

    COOKIE_DOMAIN = environ.get("COOKIE_DOMAIN", ".test.fundingservice.co.uk")
    RSA256_PRIVATE_KEY = base64.b64decode(environ.get("RSA256_PRIVATE_KEY_BASE64")).decode()
    RSA256_PUBLIC_KEY = base64.b64decode(environ.get("RSA256_PUBLIC_KEY_BASE64")).decode()

    # Session
    ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK = strtobool(getenv("ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK", "True"))
