from pathlib import Path
from typing import Any
from typing import Dict

import connexion
import prance
from api.demo.routes import build_auth_code_flow
from config import Config
from connexion.resolver import MethodViewResolver
from flask import Flask
from flask import request
from flask_assets import Environment
from flask_redis import FlaskRedis
from flask_session import Session
from flask_talisman import Talisman
from frontend.assets import compile_static_assets
from fsd_utils.logging import logging
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader

redis_mlinks = FlaskRedis(config_prefix="REDIS_MLINKS")


def get_bundled_specs(main_file: Path) -> Dict[str, Any]:
    parser = prance.ResolvingParser(main_file, strict=False)
    parser.parse()
    return parser.specification


def create_app() -> Flask:

    # Initialise Connexion Flask App
    connexion_options = {
        "swagger_path": Config.FLASK_ROOT + "/swagger/dist",
        "swagger_url": "/docs",
        "swagger_ui_template_arguments": {},
    }
    connexion_app = connexion.FlaskApp(
        "Authenticator",
        specification_dir="/openapi/",
        options=connexion_options,
    )
    connexion_app.add_api(
        get_bundled_specs(Config.FLASK_ROOT + "/openapi/api.yml"),
        validate_responses=True,
        resolver=MethodViewResolver("api"),
    )

    # Configure Flask App
    flask_app = connexion_app.app
    flask_app.config.from_object("config.Config")
    flask_app.static_folder = "frontend/static/dist/"
    flask_app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("frontend"),
            PrefixLoader(
                {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
            ),
        ]
    )
    flask_app.jinja_env.trim_blocks = True
    flask_app.jinja_env.lstrip_blocks = True
    flask_app.jinja_env.globals.update(
        _build_auth_code_flow=build_auth_code_flow
    )  # Used in template

    # Initialise logging
    logging.init_app(flask_app)

    # Initialise Sessions
    session = Session()
    session.init_app(flask_app)

    # Initialise Redis Magic Links Store
    redis_mlinks.init_app(flask_app)

    # # Configure Talisman Security Settings
    # talisman = Talisman(
    #     flask_app,
    #     strict_transport_security=Config.HSTS_HEADERS,
    #     force_https=Config.FORCE_HTTPS,
    #     content_security_policy_nonce_in=["script-src"],
    # )
    # Configure application security with Talisman
    talisman = Talisman(flask_app, **Config.TALISMAN_SETTINGS)

    # This section is needed for url_for("foo", _external=True) to
    # automatically generate http scheme when this sample is
    # running on localhost, and to generate https scheme when it is
    # deployed behind reversed proxy.
    # See also #proxy_setups section at
    # flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone
    from werkzeug.middleware.proxy_fix import ProxyFix

    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_proto=1, x_host=1)

    # Disable strict talisman on swagger docs pages
    @flask_app.before_request
    def before_request_modifier():
        if request.path.startswith("/docs"):
            talisman.content_security_policy = Config.SWAGGER_CSP
        else:
            talisman.content_security_policy = Config.SECURE_CSP

    # This is silently used by flask in the background.
    @flask_app.context_processor
    def inject_global_constants():
        return dict(
            stage="beta",
            service_title="Funding Service Design - Authenticator",
            service_meta_description=(
                "Funding Service Design Iteration - Authenticator"
            ),
            service_meta_keywords="Funding Service Design - Authenticator",
            service_meta_author="DLUHC",
        )

    with flask_app.app_context():
        from frontend.default.routes import (
            default_bp,
            not_found,
            internal_server_error,
        )
        from frontend.magic_links.routes import magic_links_bp
        from api.demo.routes import demo_bp

        flask_app.register_error_handler(404, not_found)
        flask_app.register_error_handler(500, internal_server_error)
        flask_app.register_blueprint(default_bp)
        flask_app.register_blueprint(magic_links_bp)
        flask_app.register_blueprint(demo_bp)

        # Bundle and compile assets
        assets = Environment()
        assets.init_app(flask_app)
        compile_static_assets(assets)

        return flask_app


app = create_app()
