from datetime import datetime

from config import Config
from flask import Blueprint, current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from frontend.magic_links.forms import EmailForm
from models.account import AccountError
from models.account import AccountMethods
from models.data import get_round_data
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


@magic_links_bp.route("/signed-out/<status>")
def signed_out(status):
    return (
        render_template(
            "signed_out.html",
            status=status,
            new_magic_link_url=url_for("magic_links_bp.new"),
        ),
        200,
    )


@magic_links_bp.route("/landing/<link_id>", methods=["GET"])
def landing(link_id):
    round_data = get_round_data(Config.DEFAULT_FUND_ID, Config.DEFAULT_ROUND_ID, as_dict=True)
    current_app.logger.info(round_data)
    submission_deadline = datetime.strptime(round_data.deadline, "%Y-%m-%d %X").strftime("%d %B %Y")
    return render_template(
        "landing.html",
        link_id=link_id,
        submission_deadline=submission_deadline,
        all_questions_url=Config.APPLICATION_ALL_QUESTIONS_URL
    )


@magic_links_bp.route("/new", methods=["GET", "POST"])
def new():
    """
    Returns a page containing a single question requesting the
    users email address.
    """
    # Default to COF while we only have one fund
    fund_id = request.args.get("fund_id", Config.COF_FUND_ID)
    round_id = request.args.get("round_id", Config.COF_ROUND2_ID)
    fund_round = False

    if fund_id and round_id:
        fund_round = True

    form_data = request.data
    if request.method == "GET":
        form_data = request.args

    form = EmailForm(data=form_data)

    if form.validate_on_submit():
        try:
            AccountMethods.get_magic_link(
                email=form.data.get("email"),
                fund_id=fund_id,
                round_id=round_id,
            )
            return redirect(
                url_for(
                    "magic_links_bp.check_email", email=form.data.get("email")
                )
            )
        except MagicLinkError as e:
            form.email.errors.append(str(e.message))
        except NotificationError as e:
            form.email.errors.append(str(e.message))
        except AccountError as e:
            form.email.errors.append(str(e.message))

    return render_template("email.html", form=form, fund_round=fund_round)


@magic_links_bp.route("/check-email", methods=["GET"])
def check_email():
    """
    Shows the user a message asking them to check their
    inbox for an email with a magic link
    """

    return render_template("check_email.html", email=request.args.get("email"))
