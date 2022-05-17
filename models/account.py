from dataclasses import dataclass
from typing import List

from config.env import env
from models.application import Application
from models.application import ApplicationMethods
from models.data import get_data
from models.data import post_data
from models.magic_link import MagicLinkMethods
from models.notification import Notification


@dataclass
class Account(object):
    id: str
    email: str
    applications: List[Application]

    @staticmethod
    def from_json(data: dict):
        return Account(
            id=data.get("id"),
            email=data.get("emailAddress"),
            applications=data.get("applications"),
        )


class AccountError(Exception):
    """Exception raised for errors in Account management

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Sorry, there was a problem, please try later"):
        self.message = message
        super().__init__(self.message)


class AccountMethods(Account):
    @staticmethod
    def get_account(
        email: str = None, account_id: str = None
    ) -> Account | None:
        """
        Get an account from the account store using either
        an email address or account_id.

        Args:
            email (str, optional): The account email address
            Defaults to None.
            account_id (str, optional): The account id. Defaults to None.

        Raises:
            TypeError: If both an email address or account id is given,
            a TypeError is raised.

        Returns:
            Account object or None
        """
        if email is account_id is None:
            raise TypeError("Requires an email address or account_id")

        url = env.config.get("ACCOUNT_STORE_API_HOST") + env.config.get(
            "ACCOUNTS_ENDPOINT"
        )
        params = {"email_address": email, "account_id": account_id}
        response = get_data(url, params)

        if response and "id" in response:
            return Account.from_json(response)

    @staticmethod
    def create_account(email: str) -> Account | None:
        """
        Get an account corresponding to an email_address
        or create a new account if none exists

        Args:
            email (str): The email address we wish
            to create a new account with.

        Returns:
            Account object or None
        """
        url = env.config.get("ACCOUNT_STORE_API_HOST") + env.config.get(
            "ACCOUNTS_ENDPOINT"
        )
        params = {"email_address": email}
        response = post_data(url, params)

        if response and "id" in response:
            return Account.from_json(response)

    @classmethod
    def get_magic_link(
        cls, email: str, fund_id: str = None, round_id: str = None
    ) -> bool:
        """
        Create a new magic link for a user
        and send it in a notification
        to their email address
        :param email: The user's account email address
        :param fund_id: The user's account email address
        :param round_id: The user's account email address
        :return: True if successfully created
        """
        account = cls.get_account(email)
        if not account:
            account = cls.create_account(email)
        if account:
            if fund_id and round_id:
                ApplicationMethods.create_application(
                    account.id, fund_id, round_id
                )
            new_link_json = MagicLinkMethods().create_magic_link(account)
            Notification.send(
                env.config.get("NOTIFY_TEMPLATE_MAGIC_LINK"),
                account.email,
                new_link_json.get("link"),
            )
            return True
        raise AccountError(
            message=(
                "Sorry, we couldn't create an account for this email, please"
                " contact support"
            )
        )
