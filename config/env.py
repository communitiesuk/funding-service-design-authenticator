"""
A wrapper class to enable the current app instance's environment config
to be imported in any module without requiring request context
"""


class EnvConfig:
    config = None

    def init_app(self, app):
        self.config = app.config


env = EnvConfig()
