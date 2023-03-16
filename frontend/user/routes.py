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
    """
    Route to display user status, renders user.html
    with roles_required, logged_in_user and login/
    logout urls.
    Query Args:
       - roles_required: List[str] is set by checking if
         logged_in_user
    """
    status_code = 200
    roles_required = request.args.get("roles_required")
    logged_in_user = g.user if g.is_authenticated else None
    if logged_in_user:
        if roles_required:
            if logged_in_user.roles and all(
                role_required in logged_in_user.roles
                for role_required in roles_required.upper().split("|")
            ):
                roles_required = None
            else:
                status_code = 403
    return (
        render_template(
            "user.html",
            roles_required=roles_required,
            logged_in_user=logged_in_user,
            login_url=Config.SSO_LOGIN_ENDPOINT,
            logout_url=Config.SSO_LOGOUT_ENDPOINT,
            support_mailbox=Config.SUPPORT_MAILBOX_EMAIL,
        ),
        status_code,
    )
