from unittest import mock
from unittest.mock import MagicMock

import boto3
import pytest
from fsd_utils.services.aws_extended_client import SQSExtendedClient
from moto import mock_aws

from models.notification import Config, Notification, NotificationError


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


@mock_aws
def test_notification_send_success(app_context, monkeypatch, enable_notifications):
    with mock.patch("models.notification.Notification._get_sqs_client") as mock_get_sqs_client:
        template_type = "welcome"
        template_type = "welcome"
        to_email = "test@example.com"
        content = {"name": "John"}
        sqs_extended_client = SQSExtendedClient(
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION,
            large_payload_support=Config.AWS_MSG_BUCKET_NAME,
            always_through_s3=True,
            delete_payload_from_s3=True,
            logger=MagicMock(),
        )
        s3_connection = boto3.client(
            "s3", region_name="us-east-1", aws_access_key_id="test_accesstoken", aws_secret_access_key="secret_key"
        )
        sqs_connection = boto3.client(
            "sqs", region_name="us-east-1", aws_access_key_id="test_accesstoken", aws_secret_access_key="secret_key"
        )
        s3_connection.create_bucket(Bucket=Config.AWS_MSG_BUCKET_NAME)
        queue_response = sqs_connection.create_queue(QueueName="notif-queue.fifo", Attributes={"FifoQueue": "true"})
        sqs_extended_client.sqs_client = sqs_connection
        sqs_extended_client.s3_client = s3_connection
        Config.AWS_SQS_NOTIF_APP_PRIMARY_QUEUE_URL = queue_response["QueueUrl"]
        mock_get_sqs_client.return_value = sqs_extended_client
        result = Notification.send(
            template_type, to_email, content, govuk_notify_reference="1f829816-b7e5-4cf7-bbbb-1b062e5ee399"
        )
        assert result is True


@mock_aws
def test_notification_send_failure(app_context, monkeypatch, enable_notifications):
    with mock.patch("models.notification.Notification._get_sqs_client") as mock_get_sqs_client:
        template_type = "welcome"
        to_email = "test@example.com"
        content = {"name": "John"}
        sqs_extended_client = MagicMock()
        mock_get_sqs_client.return_value = sqs_extended_client
        sqs_extended_client.submit_single_message.side_effect = Exception("SQS Error")
        with pytest.raises(NotificationError, match="Sorry, the notification could not be sent"):
            Notification.send(template_type, to_email, content)


def test_notification_error_custom_message():
    custom_message = "Custom error message"
    error = NotificationError(custom_message)

    assert str(error) == custom_message


def test_notification_error_default_message():
    error = NotificationError()

    assert str(error) == "Sorry, there was a problem please try later"
