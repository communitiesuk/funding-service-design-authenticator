from config.env import env
from models.data import post_data


class Notification(object):
    @classmethod
    def send(cls, template_type: str, to_email: str, content: dict):

        url = env.config.get("NOTIFICATION_SERVICE_HOST") + env.config.get(
            "SEND_ENDPOINT"
        )
        params = {"type": template_type, "to": to_email, "content": content}
        response = post_data(url, params)
        if response:
            return True
        raise NotificationError(
            message="Sorry, the notification could not be sent"
        )


class NotificationError(Exception):
    """Exception raised for errors in Notification management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem please try later"):
        self.message = message
        super().__init__(self.message)
