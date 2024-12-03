import json
import textwrap
from uuid import uuid4

from config import Config
from flask import current_app
from fsd_utils.config.notify_constants import NotifyConstants

NOTIFICATION_CONST = "notification"
NOTIFICATION_S3_KEY_CONST = "auth/notification"


class Notification(object):
    """
    Class for holding Notification operations
    """

    @staticmethod
    def send(template_type: str, to_email: str, content: dict, govuk_notify_reference: str | None = None):
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

        params = {
            NotifyConstants.FIELD_TYPE: template_type,
            NotifyConstants.FIELD_TO: to_email,
            NotifyConstants.FIELD_CONTENT: content,
        }
        if govuk_notify_reference:
            params["govuk_notify_reference"] = govuk_notify_reference

        try:
            sqs_extended_client = Notification._get_sqs_client()
            message_id = sqs_extended_client.submit_single_message(
                queue_url=Config.AWS_SQS_NOTIF_APP_PRIMARY_QUEUE_URL,
                message=json.dumps(params),
                message_group_id=NOTIFICATION_CONST,
                message_deduplication_id=str(uuid4()),  # ensures message uniqueness
                extra_attributes={
                    "S3Key": {
                        "StringValue": NOTIFICATION_S3_KEY_CONST,
                        "DataType": "String",
                    },
                },
            )
            current_app.logger.info(f"Message sent to SQS queue and message id is [{message_id}]")
            return True
        except Exception as e:
            current_app.logger.error("An error occurred while sending message")
            current_app.logger.error(e)
            raise NotificationError(message="Sorry, the notification could not be sent")

    @staticmethod
    def _get_sqs_client():
        sqs_extended_client = current_app.extensions["sqs_extended_client"]
        if sqs_extended_client is not None:
            return sqs_extended_client
        current_app.logger.error("An error occurred while sending message since client is not available")


class NotificationError(Exception):
    """Exception raised for errors in Notification management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem please try later"):
        self.message = message
        super().__init__(self.message)
