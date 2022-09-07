from config.envs.default import DefaultConfig
from models.fund import FundMethods


class TestFund:

    def testGetFund(self):
        fund = FundMethods.get_fund(DefaultConfig.FUND_ID_COF)
        assert DefaultConfig.FUND_ID_COF == fund.identifier, "Unexpected fund ID"
        assert "Community Ownership Fund" == fund.name, "Unexpected fund name"