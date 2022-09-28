from dataclasses import dataclass
from typing import List

from config import Config
from flask import current_app
from fsd_utils.config.notify_constants import NotifyConstants
from models.application import Application
from models.application import ApplicationMethods
from models.data import get_data
from models.data import get_round_data
from models.data import post_data
from models.fund import FundMethods
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
            id=data.get("account_id"),
            email=data.get("email_address"),
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

        url = Config.ACCOUNT_STORE_API_HOST + Config.ACCOUNTS_ENDPOINT
        params = {"email_address": email, "account_id": account_id}
        response = get_data(url, params)

        if response and "account_id" in response:
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
        url = Config.ACCOUNT_STORE_API_HOST + Config.ACCOUNTS_ENDPOINT
        params = {"email_address": email}
        response = post_data(url, params)

        if response and "account_id" in response:
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
        :param fund_id: The fund id
        :param round_id: The round id
        :return: True if successfully created
        """
        new_account = False
        account = cls.get_account(email)
        if not account:
            account = new_account = cls.create_account(email)
        if account:

            fund = FundMethods.get_fund(fund_id)
            round_for_fund = get_round_data(
                fund_id=fund_id, round_id=round_id, as_dict=True
            )

            notification_content = {
                NotifyConstants.MAGIC_LINK_REQUEST_NEW_LINK_URL_FIELD: Config.AUTHENTICATOR_HOST  # noqa
                + Config.NEW_LINK_ENDPOINT,
                NotifyConstants.MAGIC_LINK_CONTACT_HELP_EMAIL_FIELD: round_for_fund.contact_details[  # noqa
                    "email_address"
                ],  # noqa
                NotifyConstants.MAGIC_LINK_FUND_NAME_FIELD: fund.name,
            }
            if fund_id and round_id and new_account and Config.CREATE_APPLICATION_ON_ACCOUNT_CREATION:
                # Create an application if none exists
                new_application = ApplicationMethods.create_application(
                    account.id, fund_id, round_id
                )
                if new_application:
                    notification_content.update(
                        {
                            NotifyConstants.MAGIC_LINK_FUND_NAME_FIELD: new_application.fund_name  # noqa
                        }
                    )

            # Create a fresh link
            new_link_json = MagicLinkMethods().create_magic_link(account)
            notification_content.update(
                {
                    NotifyConstants.MAGIC_LINK_URL_FIELD: new_link_json.get(  # noqa
                        "link"
                    )
                }
            )

            current_app.logger.debug(
                f"Magic Link URL: {new_link_json.get('link')}"
            )
            # Send notification
            Notification.send(
                NotifyConstants.TEMPLATE_TYPE_MAGIC_LINK,
                account.email,
                notification_content,
            )
            return True

        current_app.logger.error(
            f"Could not create an account ({account}) for email '{email}'"
        )
        raise AccountError(
            message=(
                "Sorry, we couldn't create an account for this email, please"
                " contact support"
            )
        )
