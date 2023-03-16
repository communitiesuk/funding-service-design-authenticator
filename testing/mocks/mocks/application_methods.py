import pytest
from models.application import Application


class MockApplicationMethods(object):
    @staticmethod
    def create_application():
        return Application.from_json(
            {
                "application_id": "dummy-application-id",
                "fund_name": "dummy-fund-name",
                "fund_id": "dummy-fund-id",
                "round_id": "dummy-round-id",
            }
        )


@pytest.fixture()
def mock_create_application(mocker):
    mocker.patch(
        "models.application.ApplicationMethods.create_application",
        MockApplicationMethods.create_application,
    )
