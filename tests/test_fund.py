from config.envs.default import DefaultConfig
from models.fund import FundMethods


class TestFund:
    def testGetFund(self, app_context):
        fund = FundMethods.get_fund(fund_short_name="COF")
        assert (
            DefaultConfig.FUND_ID_COF == fund.identifier
        ), "Unexpected fund ID"
        assert "Community Ownership Fund" == fund.name, "Unexpected fund name"
