from flask import Blueprint
from flask import render_template
from config import Config
default_bp = Blueprint("default_bp", __name__, template_folder="templates", url_prefix=Config.URL_PREFIX)


@default_bp.route("/")
def index():
    return render_template("index.html")


@default_bp.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500
