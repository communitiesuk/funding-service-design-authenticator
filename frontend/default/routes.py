from flask import Blueprint, current_app
from flask import render_template
from config import Config

from models.data import get_round_data

default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return render_template("index.html")


@default_bp.errorhandler(404)
def not_found(error):
    current_app.logger.error(f"Encountered 404: {error}")
    round_data = get_round_data(Config.DEFAULT_FUND_ID, Config.DEFAULT_ROUND_ID, as_dict=True)
    return render_template(
        "404.html",
        contact_us_phone=round_data.contact_details["phone"],
        contact_us_email_address=round_data.contact_details["email_address"],
        contact_us_text_phone=round_data.contact_details["text_phone"],
        opening_time=round_data.support_availability["time"],
        opening_days=round_data.support_availability["days"],
        closed=round_data.support_availability["closed"]
    ), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    current_app.logger.error(f"Encountered 500: {error}")
    round_data = get_round_data(Config.DEFAULT_FUND_ID, Config.DEFAULT_ROUND_ID, as_dict=True)
    return render_template(
        "500.html",
        contact_us_phone=round_data.contact_details["phone"],
        contact_us_email_address=round_data.contact_details["email_address"],
        contact_us_text_phone=round_data.contact_details["text_phone"],
        opening_time=round_data.support_availability["time"],
        opening_days=round_data.support_availability["days"],
        closed=round_data.support_availability["closed"]
    ), 500
