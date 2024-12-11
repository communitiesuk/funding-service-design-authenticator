from flask_babel import gettext, lazy_gettext
from flask_wtf import FlaskForm
from wtforms import EmailField, HiddenField
from wtforms.validators import Email


class EmailForm(FlaskForm):
    """A Flask-WTForms class for validating a user's email address
    when creating a magic link
    """

    email = EmailField(
        "",
        validators=[Email(lazy_gettext("Enter an email address in the correct format, like name@example.com"))],
    )

    fund_id = HiddenField()
    round_id = HiddenField()

    @property
    def error_list(self):
        error_list = []
        csrf_error_message = gettext("Session expired, please refresh page to continue.")
        for key, error in self.errors.items():
            if error[0] != "The CSRF token has expired":
                error_list.append({"text": error[0], "href": "#" + key})
            else:
                error_list.append({"text": csrf_error_message})
        return error_list
