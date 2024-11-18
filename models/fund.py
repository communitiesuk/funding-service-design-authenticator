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
    def get_fund(fund_short_name: str) -> Fund:
        url = (Config.FUND_STORE_API_HOST + Config.FUND_STORE_FUND_ENDPOINT).format(fund_id=fund_short_name)
        params = {
            "language": get_lang(),
            "use_short_name": True,
        }
        response = get_data(endpoint=url, params=params)
        if response and "id" in response:
            return Fund.from_json(response)

    @staticmethod
    def get_service_name():
        short_name = request.args.get("fund")

        if short_name:
            fund_data = FundMethods.get_fund(fund_short_name=short_name)

            if fund_data:
                return fund_data.fund_title

        return None
