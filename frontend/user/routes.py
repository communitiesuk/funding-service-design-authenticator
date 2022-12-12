from config import Config
from flask import Blueprint
from flask import g
from flask import render_template
from fsd_utils.authentication.decorators import login_requested

user_bp = Blueprint(
    "user_bp",
    __name__,
    url_prefix="/service/user",
    template_folder="templates",
)


@user_bp.route("")
@login_requested
def user():
    logged_in_user = g.user if g.is_authenticated else None
    return render_template(
        "user.html",
        logged_in_user=logged_in_user,
        login_url=Config.SSO_LOGIN_ENDPOINT,
        logout_url=Config.SSO_LOGOUT_ENDPOINT,
    )