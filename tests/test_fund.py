from unittest import mock

from config.envs.default import DefaultConfig
from config.envs.unit_test import UnitTestConfig
from models.fund import Fund
from models.fund import FundMethods


class TestFund:
    def testGetFund(self, app_context):
        fund = FundMethods.get_fund(fund_short_name="COF")
        assert UnitTestConfig.FUND_ID_COF == fund.identifier, "Unexpected fund ID"
        assert "Community Ownership Fund" == fund.name, "Unexpected fund name"

    def test_get_service_name(self, app_context, mocker):
        fund_short_name = "COF"
        expected_args = {"fund_short_name": "COF"}
        # Mock get_fund with dummy dict
        mock_fund = Fund.from_json(
            {
                "id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "name": "Community Ownership Fund",
                "fund_title": "funding to save an asset in your community",
                "short_name": "COF",
                "description": "The Community Ownership Fund is a £150 million fund over 4 years to....",
            }
        )
        # Mock request object with query parameters
        mock_request = mocker.patch("models.fund.request")
        mock_request.args.get = lambda arg: fund_short_name
        # Call the method and check the output
        with mock.patch(
            "models.fund.FundMethods.get_fund",
            return_value=mock_fund,
        ) as mock_get_fund:
            FundMethods.get_service_name()
            mock_get_fund.assert_called_once_with(**expected_args)

    def test_get_service_name_for_none_short_name(self, app_context, mocker):
        fund_short_name = None
        # Mock request object with query parameters
        mock_request = mocker.patch("models.fund.request")
        mock_request.args.get = lambda arg: fund_short_name
        # Call the method and check the output
        with mock.patch(
            "models.fund.FundMethods.get_fund",
            return_value=None,
        ) as mock_get_fund:
            result = FundMethods.get_service_name()
            mock_get_fund.assert_not_called()
            assert result == (None, None)

    def test_get_fund_success(self, app_context):
        # Mock the get_data function to return a response with a valid "id"
        with mock.patch("models.fund.get_data") as mock_get_data:
            mock_get_data.return_value = {
                "id": 1234,
                "name": "Test Fund",
                "short_name": "TF",
            }

            # Call the get_fund function with a valid fund short name
            fund = FundMethods.get_fund("TF")

            # Check that the get_data function was called
            mock_get_data.assert_called_once_with(
                endpoint=(DefaultConfig.FUND_STORE_API_HOST + DefaultConfig.FUND_STORE_FUND_ENDPOINT).format(
                    fund_id="TF"
                ),
                params={"language": "en", "use_short_name": True},
            )

            # Check that the returned Fund object has the correct info
            assert fund.identifier == 1234
            assert fund.name == "Test Fund"

    def test_get_fund_failure(self, app_context):
        # Mock the get_data function to return a response with a valid "id"
        with mock.patch("models.fund.get_data") as mock_get_data:
            mock_get_data.return_value = {}

            # Call the get_fund function with a valid fund short name
            fund = FundMethods.get_fund("TF")

            # Check that the get_data function was called
            mock_get_data.assert_called_once_with(
                endpoint=(DefaultConfig.FUND_STORE_API_HOST + DefaultConfig.FUND_STORE_FUND_ENDPOINT).format(
                    fund_id="TF"
                ),
                params={"language": "en", "use_short_name": True},
            )

            # Check that the returned Fund object has the correct info
            assert fund is None
