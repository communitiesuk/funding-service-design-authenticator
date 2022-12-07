from config import Config
from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import g
from models.data import get_round_data_fail_gracefully
from fsd_utils.authentication.decorators import login_requested

default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
@login_requested
def index():
    logged_in_user = None
    if g.is_authenticated:
        logged_in_user = g.user
    return render_template(
        "index.html",
        logged_in_user=logged_in_user,
        login_url=Config.SSO_LOGIN_ENDPOINT,
        logout_url=Config.SSO_LOGOUT_ENDPOINT,
    )


@default_bp.errorhandler(404)
def not_found(error):
    current_app.logger.warning(f"Encountered 404: {error}")
    round_data = get_round_data_fail_gracefully(
        Config.DEFAULT_FUND_ID, Config.DEFAULT_ROUND_ID
    )
    return render_template("404.html", round_data=round_data), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    current_app.logger.error(f"Encountered 500: {error}")
    return (
        render_template(
            "500.html", contact_us_url=Config.APPLICANT_FRONTEND_CONTACT_US_URL
        ),
        500,
    )
