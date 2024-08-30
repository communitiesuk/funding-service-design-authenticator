from config import Config
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from frontend.magic_links.forms import EmailForm
from fsd_utils.authentication.decorators import login_requested
from models.account import AccountError
from models.account import AccountMethods
from models.data import get_round_data
from models.fund import FundMethods
from models.magic_link import MagicLinkError
from models.magic_link import MagicLinkMethods
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
            "invalid.html",
            fund=request.args.get("fund"),
            round=request.args.get("round"),
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
            fund=request.args.get("fund"),
            round=request.args.get("round"),
        ),
        200,
    )


@magic_links_bp.route("/landing/<link_id>", methods=["GET"])
@login_requested
def landing(link_id):
    """
    Returns a magic link landing page if the link_id is found
    or if it has been used or the link_id does not exist
    then redirects to the invalid link route
    :param link_id: (str) a unique single use magic link id
    :return: 200 landing page or 302 redirect
    """
    fund_short_name = request.args.get("fund")
    round_short_name = request.args.get("round")

    fund_data = FundMethods.get_fund(fund_short_name)
    round_data = get_round_data(fund_short_name, round_short_name)

    if not bool(fund_data and round_data):
        current_app.logger.warning("Fund and round information missing from query string")
        return abort(404)

    fund_short_name = fund_data.short_name
    round_short_name = round_data.short_name
    fund_name = fund_data.name
    submission_deadline = round_data.deadline
    link_key = ":".join([Config.MAGIC_LINK_RECORD_PREFIX, link_id])
    link_hash = MagicLinkMethods().redis_mlinks.get(link_key)

    show_contact_us = False
    if round_data.short_name == "R4W2" or fund_short_name == "cof-eoi":
        show_contact_us = True

    if link_hash or g.is_authenticated:
        current_app.logger.info("Rendering all questions")
        app_guidance = None
        if round_data.application_guidance:
            app_guidance = round_data.application_guidance.format(
                all_questions_url=Config.APPLICATION_ALL_QUESTIONS_URL.format(
                    fund_short_name=fund_short_name,
                    round_short_name=round_short_name,
                )
            )
        round_prospectus = round_data.prospectus if round_data.prospectus else None
        return render_template(
            "landing_eoi.html" if round_data.is_expression_of_interest else "landing.html",
            link_id=link_id,
            submission_deadline=submission_deadline,
            fund_name=fund_name,
            round_title=round_data.title,
            contact_us_email_address=round_data.contact_email,
            fund_short_name=fund_short_name,
            round_short_name=round_short_name,
            application_guidance=app_guidance,
            round_prospectus=round_prospectus,
            migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
            link_to_contact_us_page=round_data.reference_contact_page_over_email,
            show_contact_us=show_contact_us,
        )
    return redirect(
        url_for(
            "magic_links_bp.invalid",
            error="Link expired",
            fund=fund_short_name,
            round=round_short_name,
        )
    )


@magic_links_bp.route("/new", methods=["GET", "POST"])
def new():
    """
    Returns a page containing a single question requesting the
    users email address.
    """

    # Grabbing fund and round info from query params and validating
    fund_short_name = request.args.get("fund")
    round_short_name = request.args.get("round")
    fund = FundMethods.get_fund(fund_short_name)
    round = get_round_data(fund_short_name, round_short_name)

    fund_round = bool(fund_short_name and round_short_name and fund and round)
    if not fund_round:
        abort(404)

    # TODO review this code block with form_data
    form_data = request.data
    if request.method == "GET":
        form_data = request.args
    form = EmailForm(data=form_data)
    if form.validate_on_submit():
        try:
            created_link = AccountMethods.get_magic_link(
                email=form.data.get("email"),
                fund_short_name=fund_short_name,
                round_short_name=round_short_name,
            )

            if Config.AUTO_REDIRECT_LOGIN:
                current_app.logger.info(f"Auto redirecting to magic link:  {created_link}")
                return redirect(created_link)

            return redirect(
                url_for(
                    "magic_links_bp.check_email",
                    email=form.data.get("email"),
                    fund=fund_short_name,
                    round=round_short_name,
                    migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
                )
            )

        except MagicLinkError as e:
            form.email.errors.append(str(e.message))
        except NotificationError as e:
            form.email.errors.append(str(e.message))
        except AccountError as e:
            form.email.errors.append(str(e.message))

    return render_template(
        "email.html",
        form=form,
        fund_round=fund_round,
        fund_short_name=fund_short_name,
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
        is_expression_of_interest=round.is_expression_of_interest,
    )


@magic_links_bp.route("/check-email", methods=["GET"])
def check_email():
    """
    Shows the user a message asking them to check their
    inbox for an email with a magic link
    """

    return render_template(
        "check_email.html",
        email=request.args.get("email"),
        fund=request.args.get("fund"),
        round=request.args.get("round"),
        migration_banner_enabled=Config.MIGRATION_BANNER_ENABLED,
    )
