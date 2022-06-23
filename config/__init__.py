from os import environ

FLASK_ENV = environ.get("FLASK_ENV")

match FLASK_ENV:  # noqa
    case "development":
        from config.environments.development import (
            DevelopmentConfig as Config,
        )  # noqa
    case "dev":
        from config.environments.dev import (
            DevConfig as Config,
        )  # noqa
    case "test":
        from config.environments.test import (
            TestConfig as Config  # noqa
        )
    case "unit_test":
        from config.environments.unit_test import (
            UnitTestConfig as Config,
        )  # noqa
    case "production":
        pass
    case _:
        from config.environments.default import DefaultConfig as Config  # noqa

try:
    Config.pretty_print()
except AttributeError:
    print({"msg": "Config doesn't have pretty_print function."})

__all__ = [Config]
