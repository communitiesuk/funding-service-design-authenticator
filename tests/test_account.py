import pytest
from models.account import Account
from models.account import AccountMethods


id = "test_id"
email = "john@example.com"
full_name = "John Doe"
azure_ad_subject_id = "test_azure_id"
roles = []


@pytest.fixture(scope="function")
def mock_get_account(mocker, request):
    new_account = request.node.get_closest_marker("new_account")

    mocker.patch(
        "models.account.AccountMethods.get_account",
        return_value=Account.from_json(
            {
                "account_id": id,
                "email_address": email,
                "full_name": full_name,
                "azure_ad_subject_id": azure_ad_subject_id,
                "roles": roles,
            }
        )
        if not new_account
        else None,
    )
    yield


@pytest.fixture(scope="function")
def mock_create_account(mocker):

    mocker.patch(
        "models.account.post_data",
        return_value={
            "account_id": id,
            "email_address": email,
            "azure_ad_subject_id": azure_ad_subject_id,
        },
    )
    yield


@pytest.fixture(scope="function")
def mock_update_account(mocker):

    mocker.patch(
        "models.account.put_data",
        return_value={
            "account_id": id,
            "email_address": "john.Doe@example.com",
            "full_name": full_name,
            "azure_ad_subject_id": azure_ad_subject_id,
            "roles": ["COF_Lead_Assessor", "NSTF_Lead_Assessor"],
        },
    )
    yield


class TestAccountMethods(object):
    def test_create_or_update_existing_account(self, mock_get_account, mock_update_account):
        result = AccountMethods.create_or_update_account(
            email="john.Doe@example.com",
            azure_ad_subject_id="test_azure_id",
            full_name="John Doe",
            roles=["COF_Lead_Assessor", "NSTF_Lead_Assessor"],
        )
        assert result.id == id
        assert result.email == "john.Doe@example.com"
        assert result.full_name == full_name
        assert result.roles == ["COF_Lead_Assessor", "NSTF_Lead_Assessor"]
        assert result.azure_ad_subject_id == azure_ad_subject_id

    @pytest.mark.new_account(True)
    def test_create_or_update_new_account(self, mock_get_account, mock_create_account, mock_update_account):
        result = AccountMethods.create_or_update_account(
            email="john.Doe@example.com",
            azure_ad_subject_id="test_azure_id",
            full_name="John Doe",
            roles=["COF_Lead_Assessor", "NSTF_Lead_Assessor"],
        )
        assert result.id == id
        assert result.email == "john.Doe@example.com"
        assert result.full_name == full_name
        assert result.roles == ["COF_Lead_Assessor", "NSTF_Lead_Assessor"]
        assert result.azure_ad_subject_id == azure_ad_subject_id

    def test_create_account(self, mock_create_account):
        result = AccountMethods.create_account(
            email="john@example.com",
        )
        assert result.email == "john@example.com"
