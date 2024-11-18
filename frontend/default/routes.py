import traceback

from flask import Blueprint
from flask import current_app
from flask import render_template

default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return render_template("index.html")


@default_bp.errorhandler(404)
def not_found(error):
    return render_template("404.html", is_error=True), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    error_message = f"Encountered 500: {error}"
    stack_trace = traceback.format_exc()
    current_app.logger.error(f"{error_message}\n{stack_trace}")

    return render_template("500.html", is_error=True), 500
