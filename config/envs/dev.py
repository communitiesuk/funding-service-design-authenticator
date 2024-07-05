"""Flask Dev Pipeline Environment Configuration."""
import logging

from config.envs.default import DefaultConfig as Config
from fsd_utils import configclass


@configclass
class DevConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"  # pragma: allowlist secret

    # Logging
    FSD_LOG_LEVEL = logging.INFO
