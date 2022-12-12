from typing import List
from typing import Optional

import pytest

# Abbreviated sample claims that appear on the
# id_token_claims object received from Azure AD
id_token_claims = {
    "name": "Test User SSO",
    "id": 123,
    "sub": "abc",
    "preferred_username": "sso@example.com",
    "roles": [
        "LeadAssessor",
        "Assessor",
        "Commenter"
    ]
}

# Mocked accounts response from msal get_accounts method
accounts = [{"username": "test"}]

# Expected fsd-user-token claims
expected_fsd_user_token_claims = {
        "accountId": "usersso",
        "azureAdSubjectId": "abc",
        "email": "sso@example.com",
        "fullName": "Test User SSO",
        "roles": ["LEAD_ASSESSOR", "ASSESSOR", "COMMENTER"],
    }


class Account(dict):
    pass


class ConfidentialClientApplication(object):
    def acquire_token_by_auth_code_flow(
        self, auth_code_flow, auth_response, scopes=None, **kwargs
    ):
        return {
            "id_token": 1,
            "access_token": 2,
            "id_token_claims": id_token_claims,
        }

    def get_accounts(self, username=None):
        return accounts

    def acquire_token_silent(
        self,
        scopes,  # type: List[str]
        account,  # type: Optional[Account]
        authority=None,  # See get_authorization_request_url()
        force_refresh=False,  # type: Optional[bool]
        claims_challenge=None,
        **kwargs,
    ):
        return accounts


@pytest.fixture()
def mock_msal_client_application(mocker):
    mocker.patch(
        "msal.ConfidentialClientApplication.acquire_token_by_auth_code_flow",
        ConfidentialClientApplication.acquire_token_by_auth_code_flow,
    )
