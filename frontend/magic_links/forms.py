from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms import HiddenField
from wtforms.validators import DataRequired
from wtforms.validators import Email


class EmailForm(FlaskForm):
    """A Flask-WTForms class for validating a user's email address
    when creating a magic link
    """

    email = EmailField(
        "",
        description=(
            "<p>We’ll use this to confirm your email address and show your applications.</p>"
            "<p>The link will work once and stop working after 24 hours.</p>"
            "<p>If you want to return to an application, you must use the email you started the application with.</p>"
        ),
        validators=[DataRequired(), Email()],
    )
    fund_id = HiddenField()
    round_id = HiddenField()

    @property
    def error_list(self):
        error_list = []
        for key, error in self.errors.items():
            error_list.append({"text": error[0], "href": "#" + key})
        return error_list
