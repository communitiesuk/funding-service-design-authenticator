import connexion
from demo.routes import build_auth_code_flow
from flask import Flask
from flask_session import Session


def create_app() -> Flask:
    connexion_app = connexion.FlaskApp(__name__, specification_dir="openapi/")

    flask_app = connexion_app.app
    flask_app.config.from_pyfile("config.py")

    options = {
        "swagger_path": flask_app.config.get("FLASK_ROOT") + "/swagger/dist",
        "swagger_url": "/docs",
        "swagger_ui_template_arguments": {},
    }
    connexion_app.add_api("api.yaml", options=options)

    session = Session()
    session.init_app(flask_app)

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

    with flask_app.app_context():
        from demo.routes import demo_bp

        flask_app.register_blueprint(demo_bp)

    return flask_app


app = create_app()
