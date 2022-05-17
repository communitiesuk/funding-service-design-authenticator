from dataclasses import dataclass
from typing import List

from config.env import env
from models.data import get_data
from models.data import post_data


@dataclass
class Application(object):
    id: str

    @staticmethod
    def from_json(data: dict):
        return Application(
            id=data.get("id"),
        )


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

        url = env.config.get("APPLICATION_STORE_API_HOST") + env.config.get(
            "APPLICATION_STORE_APPLICATION_ENDPOINT"
        )
        params = {"application_id": application_id}
        response = get_data(url, params)

        if response and "id" in response:
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

        url = env.config.get("APPLICATION_STORE_API_HOST") + env.config.get(
            "APPLICATION_STORE_APPLICATIONS_ENDPOINT"
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
        url = env.config.get("APPLICATION_STORE_API_HOST") + env.config.get(
            "APPLICATIONS_ENDPOINT"
        )
        params = {
            "account_id": account_id,
            "fund_id": fund_id,
            "round_id": round_id,
        }
        response = post_data(url, params)

        if response and "id" in response:
            return Application.from_json(response)
