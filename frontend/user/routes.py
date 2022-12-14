from config import Config
from flask import Blueprint
from flask import g
from flask import render_template
from flask import request
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
    roles_required = request.args.get("roles_required")
    print(g.is_authenticated)
    logged_in_user = g.user if g.is_authenticated else None
    roles_error = False
    if logged_in_user and (
        not logged_in_user.roles
        or not all(
            role_required in logged_in_user.roles
            for role_required in roles_required
        )
    ):
        roles_error = True
    print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
    return render_template(
        "user.html",
        roles_error=roles_error,
        roles_required=roles_required,
        logged_in_user=logged_in_user,
        login_url=Config.SSO_LOGIN_ENDPOINT,
        logout_url=Config.SSO_LOGOUT_ENDPOINT,
    )
