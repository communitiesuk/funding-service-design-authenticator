from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.validators import DataRequired
from wtforms.validators import Email


class EmailForm(FlaskForm):
    """A Flask-WTForms class for validating a user's email address
    when creating a magic link
    """

    email = EmailField(
        "Please enter your email address",
        description="eg. a@example.com",
        validators=[DataRequired(), Email()],
    )

    @property
    def error_list(self):
        error_list = []
        for key, error in self.errors.items():
            error_list.append({"text": error[0], "href": "#" + key})
        return error_list
