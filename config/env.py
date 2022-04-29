class EnvConfig:
    config = None

    def init_app(self, app):
        self.config = app.config


env = EnvConfig()
