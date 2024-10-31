from copy import deepcopy
from os import getenv
from pathlib import Path
from typing import Any
from typing import Dict

import connexion
import prance
import static_assets
from config import Config
from connexion.resolver import MethodViewResolver
from flask import Flask
from flask import request
from flask_assets import Environment
from flask_babel import Babel
from flask_babel import gettext
from flask_redis import FlaskRedis
from flask_session import Session
from flask_talisman import Talisman
from frontend.magic_links.filters import datetime_format
from fsd_utils import init_sentry
from fsd_utils import LanguageSelector
from fsd_utils.healthchecks.checkers import FlaskRunningChecker
from fsd_utils.healthchecks.checkers import RedisChecker
from fsd_utils.healthchecks.healthcheck import Healthcheck
from fsd_utils.locale_selector.get_lang import get_lang
from fsd_utils.logging import logging
from fsd_utils.services.aws_extended_client import SQSExtendedClient
from jinja2 import ChoiceLoader
from jinja2 import PackageLoader
from jinja2 import PrefixLoader
from models.fund import FundMethods

redis_mlinks = FlaskRedis(config_prefix="REDIS_MLINKS")


def get_bundled_specs(main_file: Path) -> Dict[str, Any]:
    parser = prance.ResolvingParser(main_file, strict=False)
    parser.parse()
    return parser.specification


def create_app() -> Flask:
    init_sentry()

    # Initialise Connexion Flask App
    connexion_options = Config.CONNEXION_OPTIONS
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
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
        ]
    )
    flask_app.jinja_env.trim_blocks = True
    flask_app.jinja_env.lstrip_blocks = True
    flask_app.jinja_env.globals["get_lang"] = get_lang

    # Initialise logging
    logging.init_app(flask_app)

    # Initialize sqs extended client
    create_sqs_extended_client(flask_app)
    # Initialise Sessions
    session = Session()
    session.init_app(flask_app)

    # Initialise Redis Magic Links Store
    redis_mlinks.init_app(flask_app)

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

    babel = Babel(flask_app)
    babel.locale_selector_func = get_lang
    LanguageSelector(flask_app)

    # Disable strict talisman on swagger docs pages
    @flask_app.before_request
    def before_request_modifier():
        if request.path.startswith("/docs"):
            talisman.content_security_policy = Config.SWAGGER_CSP
            talisman.content_security_policy_nonce_in = ["None"]
        else:
            secure_csp = deepcopy(Config.SECURE_CSP)
            # allow inline script related to handling cookies
            secure_csp["script-src"].append("'sha256-qJr6rnZIepboaF/c9sFdugAE+I8xpVXVPeO/lk7/Yj0='")
            talisman.content_security_policy = secure_csp

    # This is silently used by flask in the background.
    @flask_app.context_processor
    def inject_global_constants():
        fund = request.args.get("fund", "")
        round = request.args.get("round", "")
        return dict(
            stage="beta",
            service_meta_author="Department for Levelling up Housing and Communities",
            accessibility_statement_url=Config.APPLICANT_FRONTEND_HOST + "/accessibility_statement",  # noqa
            cookie_policy_url=Config.APPLICANT_FRONTEND_HOST + "/cookie_policy",
            contact_us_url=f"{Config.APPLICANT_FRONTEND_HOST}/contact_us?fund={fund}&round={round}",
            privacy_url=Config.APPLICANT_FRONTEND_HOST
            + "/privacy"
            + f"?fund={request.args.get('fund', '')}&round={request.args.get('round', '')}",
            feedback_url=Config.APPLICANT_FRONTEND_HOST
            + "/feedback"
            + f"?fund={request.args.get('fund', '')}&round={request.args.get('round', '')}",
        )

    @flask_app.context_processor
    def inject_service_name():
        fund_title, fund_name = FundMethods.get_service_name()
        if fund_title:
            service_title = gettext("Apply for") + " " + fund_title
        elif return_app := request.args.get("return_app"):
            service_title = Config.SAFE_RETURN_APPS[return_app].service_title
        else:
            service_title = "Access Funding"
        return dict(
            service_title=service_title,
            fund_name=fund_name,
        )

    with flask_app.app_context():
        from frontend.default.routes import (
            default_bp,
            not_found,
            internal_server_error,
        )
        from frontend.magic_links.routes import magic_links_bp
        from frontend.sso.routes import sso_bp
        from frontend.user.routes import user_bp

        flask_app.register_error_handler(404, not_found)
        flask_app.register_error_handler(500, internal_server_error)
        flask_app.register_blueprint(default_bp)
        flask_app.register_blueprint(magic_links_bp)
        flask_app.register_blueprint(sso_bp)
        flask_app.register_blueprint(user_bp)
        flask_app.jinja_env.filters["datetime_format"] = datetime_format

        # Bundle and compile assets
        assets = Environment()
        assets.init_app(flask_app)

        static_assets.init_assets(
            flask_app,
            auto_build=Config.ASSETS_AUTO_BUILD,
            static_folder=Config.STATIC_FOLDER,
        )

        health = Healthcheck(flask_app)
        health.add_check(FlaskRunningChecker())
        health.add_check(RedisChecker(redis_mlinks))

        return flask_app


def create_sqs_extended_client(flask_app):
    if (
        getenv("AWS_ACCESS_KEY_ID", "Access Key Not Available") == "Access Key Not Available"
        and getenv("AWS_SECRET_ACCESS_KEY", "Secret Key Not Available") == "Secret Key Not Available"
    ):
        flask_app.extensions["sqs_extended_client"] = SQSExtendedClient(
            region_name=Config.AWS_REGION,
            endpoint_url=getenv("AWS_ENDPOINT_OVERRIDE", None),
            large_payload_support=Config.AWS_MSG_BUCKET_NAME,
            always_through_s3=True,
            delete_payload_from_s3=True,
            logger=flask_app.logger,
        )
    else:
        flask_app.extensions["sqs_extended_client"] = SQSExtendedClient(
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION,
            endpoint_url=getenv("AWS_ENDPOINT_OVERRIDE", None),
            large_payload_support=Config.AWS_MSG_BUCKET_NAME,
            always_through_s3=True,
            delete_payload_from_s3=True,
            logger=flask_app.logger,
        )


app = create_app()
