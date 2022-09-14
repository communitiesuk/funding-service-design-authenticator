from flask import Blueprint, current_app
from flask import render_template
from config import Config

from models.data import get_round_data_fail_gracefully

default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return render_template("index.html")


@default_bp.errorhandler(404)
def not_found(error):
    current_app.logger.warning(f"Encountered 404: {error}")
    round_data = get_round_data_fail_gracefully(Config.DEFAULT_FUND_ID, Config.DEFAULT_ROUND_ID)
    return render_template("404.html", round_data=round_data), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    current_app.logger.error(f"Encountered 500: {error}")
    return render_template("500.html"), 500
