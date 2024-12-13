from flask import Blueprint, render_template, request, url_for

sso_bp = Blueprint(
    "sso_bp",
    __name__,
    url_prefix="/service/sso",
    template_folder="templates",
)


@sso_bp.route("/signed-out/<status>")
def signed_out(status):
    return_app = request.args.get("return_app")
    return_path = request.args.get("return_path")
    return (
        render_template(
            "sso_signed_out.html",
            status=status,
            login_url=url_for("api_sso.login", return_app=return_app, return_path=return_path),
        ),
        200,
    )
