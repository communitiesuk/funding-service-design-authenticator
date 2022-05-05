import connexion
from api.demo.routes import build_auth_code_flow
from config.env import env
from connexion.resolver import MethodViewResolver
from flask import Flask
from flask import request
from flask_redis import FlaskRedis
from flask_session import Session
from flask_talisman import Talisman

redis_mlinks = FlaskRedis(config_prefix="REDIS_MLINKS")


def create_app(testing=False) -> Flask:
    connexion_app = connexion.FlaskApp(__name__, specification_dir="")

    flask_app = connexion_app.app
    if testing:
        flask_app.config.from_object("config.environments.local.LocalConfig")
    else:
        flask_app.config.from_object("config.Config")

    options = {
        "swagger_path": flask_app.config.get("FLASK_ROOT") + "/swagger/dist",
        "swagger_url": "/docs",
        "swagger_ui_template_arguments": {},
    }
    connexion_app.add_api(
        "api.yaml", options=options, resolver=MethodViewResolver("api")
    )

    session = Session()
    session.init_app(flask_app)

    redis_mlinks.init_app(flask_app)

    # This is needed to access the running app's environment config
    # outside the request context using env.config.get("VARIABLE_NAME")
    env.init_app(flask_app)

    talisman = Talisman(
        flask_app,
        strict_transport_security=env.config.get("HSTS_HEADERS"),
        force_https=env.config.get("FORCE_HTTPS"),
    )

    # This section is needed for url_for("foo", _external=True) to
    # automatically generate http scheme when this sample is
    # running on localhost, and to generate https scheme when it is
    # deployed behind reversed proxy.
    # See also #proxy_setups section at
    # flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone
    from werkzeug.middleware.proxy_fix import ProxyFix

    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_proto=1, x_host=1)

    flask_app.jinja_env.globals.update(
        _build_auth_code_flow=build_auth_code_flow
    )  # Used in template

    # Disable strict talisman on swagger docs pages
    @flask_app.before_request
    def before_request_modifier():
        if request.path.startswith("/docs"):
            talisman.content_security_policy = env.config.get("SWAGGER_CSP")
        else:
            talisman.content_security_policy = env.config.get("STRICT_CSP")

    with flask_app.app_context():
        from api.demo.routes import demo_bp

        flask_app.register_blueprint(demo_bp)

    return flask_app


app = create_app()
