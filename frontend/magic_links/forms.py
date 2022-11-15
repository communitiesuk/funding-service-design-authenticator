from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms import HiddenField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from flask_babel import gettext
from flask_babel import _

class EmailForm(FlaskForm):
    """A Flask-WTForms class for validating a user's email address
    when creating a magic link
    """

    email = EmailField(
        "",
        validators=[
            DataRequired(
                "Enter an email address in the correct format, like"
                " name@example.com"
            ),
            Email(),
        ],
    )
    fund_id = HiddenField()
    round_id = HiddenField()

    @property
    def error_list(self):
        error_list = []
        csrf_error_message = (
            "Session expired, please refresh page to continue."
        )
        for key, error in self.errors.items():
            if error[0] != "The CSRF token has expired":
                error_list.append({"text": error[0], "href": "#" + key})
            else:
                error_list.append({"text": csrf_error_message})
        return error_list
