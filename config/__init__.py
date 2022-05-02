from os import environ

FLASK_ENV = environ.get("FLASK_ENV")

if FLASK_ENV == "development":
    from config.development import DevelopmentConfig as Config
elif FLASK_ENV == "test":
    from config.test import TestConfig as Config
elif FLASK_ENV == "production":
    from config.production import ProductionConfig as Config
else:
    from config.default import Config  # noqa
