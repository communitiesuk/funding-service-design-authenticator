"""Flask Dev Pipeline Environment Configuration."""

import logging

from fsd_utils import configclass

from config.envs.default import DefaultConfig as Config


@configclass
class DevConfig(Config):
    #  Application Config
    SECRET_KEY = "dev"  # pragma: allowlist secret

    # Logging
    FSD_LOG_LEVEL = logging.INFO
