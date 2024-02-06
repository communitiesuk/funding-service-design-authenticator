import pytest
from models.notification import Config
from models.notification import Notification
from models.notification import NotificationError


@pytest.fixture
def disable_notifications(monkeypatch):
    monkeypatch.setattr(Config, "DISABLE_NOTIFICATION_SERVICE", True)


@pytest.fixture
def enable_notifications(monkeypatch):
    monkeypatch.setattr(Config, "DISABLE_NOTIFICATION_SERVICE", False)


def test_notification_send_disabled(app_context, disable_notifications, caplog):
    template_type = "welcome"
    to_email = "test@example.com"
    content = {"name": "John"}

    result = Notification.send(template_type, to_email, content)

    assert result is True
    assert "Notification service is disabled" in caplog.text


def test_notification_send_success(app_context, monkeypatch, enable_notifications):
    monkeypatch.setattr("models.notification.post_data", lambda *_: True)

    template_type = "welcome"
    to_email = "test@example.com"
    content = {"name": "John"}

    result = Notification.send(template_type, to_email, content)

    assert result is True


def test_notification_send_failure(monkeypatch, enable_notifications):
    monkeypatch.setattr("models.notification.post_data", lambda *_: False)

    template_type = "welcome"
    to_email = "test@example.com"
    content = {"name": "John"}

    with pytest.raises(NotificationError, match="Sorry, the notification could not be sent"):
        Notification.send(template_type, to_email, content)


def test_notification_error_custom_message():
    custom_message = "Custom error message"
    error = NotificationError(custom_message)

    assert str(error) == custom_message


def test_notification_error_default_message():
    error = NotificationError()

    assert str(error) == "Sorry, there was a problem please try later"
