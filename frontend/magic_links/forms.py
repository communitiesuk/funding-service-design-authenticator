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
            "We’ll use this to confirm your email address and show your"
            " applications."
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
