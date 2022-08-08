from flask import Blueprint
from flask import render_template
from config import Config


default_bp = Blueprint("default_bp", __name__, template_folder="templates")


@default_bp.route("/")
def index():
    return render_template("index.html",
                           accessibility_statement_url=Config.APPLICANT_FRONTEND_ACCESSIBILITY_STATEMENT_URL,
                           cookie_policy_url=Config.APPLICANT_FRONTEND_COOKIE_POLICY_URL)


@default_bp.errorhandler(404)
def not_found(error):
    return render_template("404.html",
                           accessibility_statement_url=Config.APPLICANT_FRONTEND_ACCESSIBILITY_STATEMENT_URL,
                           cookie_policy_url=Config.APPLICANT_FRONTEND_COOKIE_POLICY_URL), 404


@default_bp.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html",
                           accessibility_statement_url=Config.APPLICANT_FRONTEND_ACCESSIBILITY_STATEMENT_URL,
                           cookie_policy_url=Config.APPLICANT_FRONTEND_COOKIE_POLICY_URL), 500
