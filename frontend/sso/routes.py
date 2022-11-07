from config import Config
from flask import Blueprint
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

sso_bp = Blueprint(
    "sso_bp",
    __name__,
    url_prefix="/service/sso",
    template_folder="templates",
)


@sso_bp.route("/signed-out/<status>")
def signed_out(status):
    return (
        render_template(
            "sso_signed_out.html",
            status=status,
            login_url=Config.SSO_LOGIN_ENDPOINT,
        ),
        200,
    )