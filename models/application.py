from dataclasses import dataclass
from typing import List

from config import Config
from models.data import get_data
from models.data import post_data


@dataclass
class Application(object):
    application_id: str
    fund_name: str
    fund_id: str
    round_id: str

    @staticmethod
    def from_json(data: dict):
        return Application(
            application_id=data.get("application_id"),
            fund_name=data.get("fund_name"),
            fund_id=data.get("fund_id"),
            round_id=data.get("round_id"),
        )


class ApplicationError(Exception):
    """Exception raised for errors in Application management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem, please try later"):
        self.message = message
        super().__init__(self.message)


class ApplicationMethods(Application):
    @staticmethod
    def get_application(application_id: str) -> Application | None:
        """
        Get application from the application store with application_id.

        Args:
            application_id (str): The application_id

        Returns:
            List of Applications
        """

        url = (
            Config.APPLICATION_STORE_API_HOST
            + Config.APPLICATION_STORE_APPLICATION_ENDPOINT
        )
        params = {"application_id": application_id}
        response = get_data(url, params)

        if response and "application_id" in response:
            return Application.from_json(response)

    @staticmethod
    def get_applications(
        account_id: str, **kwargs
    ) -> List[Application] | None:
        """
        Get applications from the application store matching given params.

        Args:
            account_id (str): The account id.

        Returns:
            List of Applications
        """
        if account_id is None:
            raise TypeError("Requires an account_id")

        url = (
            Config.APPLICATION_STORE_API_HOST
            + Config.APPLICATION_STORE_APPLICATIONS_ENDPOINT
        )
        response = get_data(url, kwargs)

        if response:
            return [Application.from_json(item) for item in response]

    @staticmethod
    def create_application(
        account_id: str, fund_id: str, round_id: str
    ) -> Application | None:
        """
        Create an application corresponding to a
        given email_address, fund_id and round_id

        Args:
            account_id (str): The account_id to create an application for
            fund_id (str): The fund_id of the fund applying for
            round_id (str): The round_id of the round applying for

        Returns:
            Application object or None
        """
        url = Config.APPLICATION_STORE_API_HOST + Config.APPLICATIONS_ENDPOINT
        params = {
            "account_id": account_id,
            "fund_id": fund_id,
            "round_id": round_id,
        }
        response = post_data(url, params)

        if response and "application_id" in response:
            return Application.from_json(response)
