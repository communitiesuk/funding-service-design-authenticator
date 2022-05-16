from config.env import env
from flask import Blueprint
from flask import render_template

magic_links_bp = Blueprint(
    "magic_links_bp",
    __name__,
    url_prefix="/service/magic-links",
    template_folder="templates",
)


@magic_links_bp.route("/invalid")
def invalid():
    new_magic_link_url = env.config.get("NEW_MAGIC_LINK_URL")

    return (
        render_template("invalid.html", new_magic_link_url=new_magic_link_url),
        403,
    )
