from flask import Blueprint, g, render_template, request, url_for
from fsd_utils.authentication.decorators import login_requested

from config import Config

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
                role_required in logged_in_user.roles for role_required in roles_required.upper().split("|")
            ):
                roles_required = None
            else:
                status_code = 403
    return (
        render_template(
            "user.html",
            roles_required=roles_required,
            logged_in_user=logged_in_user,
            login_url=url_for("api_sso_routes_SsoView_login"),
            logout_url=url_for("api_sso_routes_SsoView_logout_get"),
            support_mailbox=Config.SUPPORT_MAILBOX_EMAIL,
        ),
        status_code,
    )
