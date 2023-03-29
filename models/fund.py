from dataclasses import dataclass
from typing import List

from config import Config
from flask import request
from fsd_utils.locale_selector.get_lang import get_lang
from models.data import get_data
from models.round import Round


@dataclass
class Fund:
    name: str
    fund_title: str
    short_name: str
    identifier: str
    description: str
    rounds: List[Round] = None

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            fund_title=data.get("title"),
            short_name=data.get("short_name"),
            identifier=data.get("id"),
            description=data.get("description"),
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)


class FundMethods:
    @staticmethod
    def get_fund(fund_id: str = None, fund_short_name: str = None) -> Fund:
        fund_short_name = request.args.get("fund", fund_short_name)
        if fund_short_name:
            url = (
                Config.FUND_STORE_API_HOST + Config.FUND_STORE_FUND_ENDPOINT
            ).format(fund_id=fund_short_name)
        # TODO remove after R2W3 closes and fs-2505 is complete (make fund_short_name non-optional) # noqa
        else:
            url = (
                Config.FUND_STORE_API_HOST + Config.FUND_STORE_FUND_ENDPOINT
            ).format(fund_id=fund_id)

        params = {
            "language": get_lang(),
            "use_short_name": True if fund_short_name else False,
        }
        response = get_data(endpoint=url, params=params)

        if response and "id" in response:
            return Fund.from_json(response)
