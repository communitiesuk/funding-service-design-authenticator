import traceback

from config import Config
from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import request
from models.data import get_round_data_fail_gracefully

default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return render_template("index.html")


@default_bp.errorhandler(404)
def not_found(error):
    current_app.logger.warning(f"Encountered 404 against url {request.path}: {error}")
    fund_short_name = request.args.get("fund")
    round_short_name = request.args.get("round")
    round_data = get_round_data_fail_gracefully(fund_short_name, round_short_name, True)
    return render_template("404.html", round_data=round_data), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    error_message = f"Encountered 500: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.error(f"{error_message}\n{stack_trace}")
    return (
        render_template(
            "500.html",
            contact_us_url=Config.APPLICANT_FRONTEND_HOST
            + "/contact_us"
            + f"?fund={request.args.get('fund', '')}&round={request.args.get('round', '')}",
        ),
        500,
    )
