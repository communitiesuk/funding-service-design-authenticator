from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from frontend.magic_links.forms import EmailForm
from models.account import AccountError
from models.account import AccountMethods
from models.magic_link import MagicLinkError
from models.notification import NotificationError

magic_links_bp = Blueprint(
    "magic_links_bp",
    __name__,
    url_prefix="/service/magic-links",
    template_folder="templates",
)


@magic_links_bp.route("/invalid")
def invalid():

    return (
        render_template(
            "invalid.html", new_magic_link_url=url_for("magic_links_bp.new")
        ),
        403,
    )


@magic_links_bp.route("/new", methods=["GET", "POST"])
def new():
    """
    Returns a page containing a single question requesting the
    users email address.
    """
    form = EmailForm(data=request.data)

    fund_id = request.args.get("fund_id")
    round_id = request.args.get("round_id")

    if form.validate_on_submit():
        try:
            AccountMethods.get_magic_link(
                email=form.data.get("email"),
                fund_id=fund_id,
                round_id=round_id,
            )
            return redirect(url_for("magic_links_bp.check_email"))
        except MagicLinkError as e:
            form.email.errors.append(str(e.message))
        except NotificationError as e:
            form.email.errors.append(str(e.message))
        except AccountError as e:
            form.email.errors.append(str(e.message))

    return render_template("email.html", form=form)


@magic_links_bp.route("/check-email", methods=["GET"])
def check_email():
    """
    Shows the user a message asking them to check their
    inbox for an email with a magic link
    """

    return render_template("check_email.html")
