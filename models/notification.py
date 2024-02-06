import json
import textwrap

from config import Config
from flask import current_app
from fsd_utils.config.notify_constants import NotifyConstants
from models.data import post_data


class Notification(object):
    """
    Class for holding Notification operations
    """

    @staticmethod
    def send(template_type: str, to_email: str, content: dict):
        """
        Sends a notification using the Gov.UK Notify Service

        Args:
            template_type: (str) A key of the template to use in the
                DLUHC notifications service (which maps to a
                Notify Service template key)
            to_email: (str) The email to send the notification to
            content: (dict) A dictionary of content to send to
                fill out the notification template
        """

        if Config.DISABLE_NOTIFICATION_SERVICE:
            template_msg = textwrap.dedent(
                f"""
                Notification service is disabled, details below:
                - Template type: {template_type}
                - To email: {to_email}
                - Content:
            """
            )
            current_app.logger.info(f"{template_msg}{json.dumps(content, indent=4)}")
            return True

        url = Config.NOTIFICATION_SERVICE_HOST + Config.SEND_ENDPOINT
        params = {
            NotifyConstants.FIELD_TYPE: template_type,
            NotifyConstants.FIELD_TO: to_email,
            NotifyConstants.FIELD_CONTENT: content,
        }
        response = post_data(url, params)
        if response:
            return True
        raise NotificationError(message="Sorry, the notification could not be sent")


class NotificationError(Exception):
    """Exception raised for errors in Notification management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem please try later"):
        self.message = message
        super().__init__(self.message)
