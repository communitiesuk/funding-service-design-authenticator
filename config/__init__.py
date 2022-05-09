from os import environ

FLASK_ENV = environ.get("FLASK_ENV")

if FLASK_ENV == "local":
    from config.environments.development import DevelopmentConfig as Config
elif FLASK_ENV == "dev":
    from config.environments.dev import DevConfig as Config
elif FLASK_ENV == "test":
    from config.environments.test import TestConfig as Config
elif FLASK_ENV == "production":
    from config.environments.production import ProductionConfig as Config
else:
    from config.environments.default import Config  # noqa
