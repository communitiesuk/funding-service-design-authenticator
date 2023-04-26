from unittest import mock

import pytest
from config import Config
from config.envs.default import DefaultConfig
from models.fund import Fund
from models.fund import FundMethods


class TestFund:
    def testGetFund(self, app_context):
        fund = FundMethods.get_fund(fund_short_name="COF")
        assert (
            DefaultConfig.FUND_ID_COF == fund.identifier
        ), "Unexpected fund ID"
        assert "Community Ownership Fund" == fund.name, "Unexpected fund name"

    @pytest.mark.parametrize(
        "short_name, expected_arg",
        [
            ("COF", {"fund_short_name": "COF"}),
            (
                None,
                {"fund_id": Config.DEFAULT_FUND_ID, "use_short_name": False},
            ),
        ],
    )
    def test_get_service_name(
        self, app_context, short_name, expected_arg, mocker
    ):

        # Mock get_fund with dummy dict
        mock_fund = Fund.from_json(
            {
                "id": "47aef2f5-3fcb-4d45-acb5-f0152b5f03c4",
                "name": "Community Ownership Fund",
                "fund_title": "funding to save an asset in your community",
                "short_name": "COF",
                "description": (
                    "The Community Ownership Fund is a £150 million fund over"
                    " 4 years to...."
                ),
            }
        )

        # Mock request object with query parameters
        mock_request = mocker.patch("models.fund.request")
        mock_request.args.get = lambda arg: short_name

        # Call the method and check the output
        with mock.patch(
            "models.fund.FundMethods.get_fund",
            return_value=mock_fund,
        ) as mock_get_fund:
            FundMethods.get_service_name()
            mock_get_fund.assert_called_once_with(**expected_arg)
