from config import Config
from flask import Blueprint
from flask import current_app
from flask import render_template
from models.data import get_round_data_fail_gracefully
from models.fund import FundMethods

default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return render_template("index.html")


@default_bp.errorhandler(404)
def not_found(error):
    current_app.logger.warning(f"Encountered 404: {error}")
    round_data = get_round_data_fail_gracefully(
        Config.DEFAULT_FUND_ID, Config.DEFAULT_ROUND_ID
    )
    fund_data = FundMethods.get_fund()
    if fund_data:
        fund_title = fund_data.fund_title
    else:
        # hardcoded fund name and else statement to be deleted
        # when round 2 is closed.
        # because the fund title will be retrieved through fund_short_name arg
        fund_title = "funding to save an asset in your community"
    return (
        render_template(
            "404.html", round_data=round_data, fund_title=fund_title
        ),
        404,
    )


@default_bp.errorhandler(500)
def internal_server_error(error):
    current_app.logger.error(f"Encountered 500: {error}")
    fund_data = FundMethods.get_fund()

    if fund_data:
        fund_title = fund_data.fund_title
    else:
        # hardcoded fund name and else statement to be deleted
        # when round 2 is closed.
        # because the fund title will be retrieved through fund_short_name arg.
        fund_title = "funding to save an asset in your community"
    return (
        render_template(
            "500.html",
            fund_title=fund_title,
            contact_us_url=Config.APPLICANT_FRONTEND_CONTACT_US_URL,
        ),
        500,
    )
