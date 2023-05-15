"""Flask Local Development Environment Configuration."""
import logging
from os import getenv

import redis
from config.envs.default import DefaultConfig as Config
from distutils.util import strtobool
from fsd_utils import configclass

# these are only used for unit tests & development, so it's okay to commit them
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgHGbtF1yVGW+rCAFOIdakUVwCfuvxHE38lE/i0KWpMwdSHZFFLYn
HjBVOOh15EiizYza4FTJTMvL2E4QrLpqYj6KE6tvHrhyP/N5fypSzt8vCj9spZ8+
0kFucW9zyMkPuDisYtmkWGdxBmkd3gtYp3mOI53VVDgKbtoIFU3sIk5NAgMBAAEC
gYBXIXrgXGocKnNqj3Z+YNifr8EIVhLMXoMrCxgsNssnfKHxiyPKXBAMM6BUsO4n
Qy1whQGeJVEP0EQSAznmMucrWAYol+ve95LgXtrLEWPtetq/oU/boqcSFIY2jy45
P0DqJ556D2kCMvYOzY/SnLqVUOM8KNOl5/I2851i1jmIIQJBALEOkKVnNwG4FHPj
UUbQ/+MjB6rZBS9j5vtpszZvsv9kmgLzI3UNqtv7C0gtCY4Pg20+3Q93bTYLEUtJ
sIXdxtkCQQCkQwzaPzwx84bRrsOwqQe82VtRSFtcOlz6Rhic+V9WXM+ZjCTCRsqZ
T6rtcBkmsCIymEIDRbQe/+WJDT5fUuKVAkA0Y9rpFmFwYMesgtbJ3Y3Z58OdCho+
q5DtU5lzwhl0+I+Zz9fuCt1DukTcVnc9UdnRuYgvy2bFVwEHBgb1lWoBAkAddnVY
tBzs7LxS4eDxz++2XNo3Qx439bP1pBsIFOaXy//kj7GMMzxlsVd8TS4FtXP81TiJ
87eyE74tDfYRDQHdAkEAhSbPlRcQSwEom57cFY3tWznRUM3ox+B56txlCjX1JpiX
XP9m718FpBtSWq+4gs0yAoLujZyK9BoWvEmqrm6O8Q==
-----END RSA PRIVATE KEY-----"""
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGeMA0GCSqGSIb3DQEBAQUAA4GMADCBiAKBgHGbtF1yVGW+rCAFOIdakUVwCfuv
xHE38lE/i0KWpMwdSHZFFLYnHjBVOOh15EiizYza4FTJTMvL2E4QrLpqYj6KE6tv
HrhyP/N5fypSzt8vCj9spZ8+0kFucW9zyMkPuDisYtmkWGdxBmkd3gtYp3mOI53V
VDgKbtoIFU3sIk5NAgMBAAE=
-----END PUBLIC KEY-----
"""


@configclass
class UnitTestConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"
    COOKIE_DOMAIN = None

    # Logging
    FSD_LOG_LEVEL = logging.DEBUG

    # Hostname for this service
    AUTHENTICATOR_HOST = "http://localhost:5000"

    # Azure Active Directory Config
    AZURE_AD_CLIENT_ID = "abc"
    AZURE_AD_CLIENT_SECRET = "123"
    AZURE_AD_TENANT_ID = "organizations"
    AZURE_AD_AUTHORITY = (
        # consumers|organizations|<tenant_id>
        # - signifies the Azure AD tenant endpoint
        "https://login.microsoftonline.com/"
        + AZURE_AD_TENANT_ID
    )

    # The absolute URL must match the redirect URI you set
    # in the app's registration in the Azure portal.
    AZURE_AD_REDIRECT_URI = AUTHENTICATOR_HOST + Config.AZURE_AD_REDIRECT_PATH

    SESSION_TYPE = (
        # Specifies how the token cache should be stored
        # in server-side session
        # "filesystem"
        "redis"
    )
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False
    ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK = strtobool(
        getenv("ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK", "False")
    )

    RSA256_PRIVATE_KEY = PRIVATE_KEY
    RSA256_PUBLIC_KEY = PUBLIC_KEY

    # Redis
    REDIS_MLINKS_URL = "redis://localhost:6379/0"
    REDIS_SESSIONS_URL = "redis://localhost:6379/1"
    SESSION_REDIS = redis.from_url(REDIS_SESSIONS_URL)

    # APIs
    APPLICATION_STORE_API_HOST = "application_store"
    ACCOUNT_STORE_API_HOST = "account_store"
    NOTIFICATION_SERVICE_HOST = "notification_service"

    # Security
    Config.TALISMAN_SETTINGS["force_https"] = False
    WTF_CSRF_ENABLED = False

    APPLICANT_FRONTEND_HOST = "frontend"
    APPLICANT_FRONTEND_ACCESSIBILITY_STATEMENT_URL = "/accessibility_statement"
    APPLICANT_FRONTEND_COOKIE_POLICY_URL = "/cookie_policy"

    # Assessment Frontend
    ASSESSMENT_FRONTEND_HOST = ""
    ASSESSMENT_POST_LOGIN_URL = ""
