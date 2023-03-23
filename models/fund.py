from dataclasses import dataclass
from typing import List

from config import Config
from fsd_utils.locale_selector.get_lang import get_lang
from models.data import get_data
from models.round import Round


@dataclass
class Fund:
    name: str
    title: str
    short_name: str
    identifier: str
    description: str
    rounds: List[Round] = None

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            title = data.get("title"),
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
    def get_fund(fund_id: str) -> Fund:
        url = (
            Config.FUND_STORE_API_HOST + Config.FUND_STORE_FUND_ENDPOINT
        ).format(fund_id=fund_id)

        language = {"language": get_lang()}
        response = get_data(endpoint=url, params=language)
        if response and "id" in response:
            return Fund.from_json(response)
