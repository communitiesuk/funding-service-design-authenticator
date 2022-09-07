from cgitb import reset
from dataclasses import dataclass
from models.data import get_data
from typing import List

from models.round import Round

from config import Config


@dataclass
class Fund:
    name: str
    identifier: str
    description: str
    contact_help: str
    rounds: List[Round] = None

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            identifier=data.get("id"),
            description=data.get("description"),
            contact_help=data.get("contact_email"),
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)

class FundMethods:
    @staticmethod
    def get_fund(fund_id: str) -> Fund:
        url = (Config.FUND_STORE_API_HOST + Config.FUND_STORE_FUND_ENDPOINT).format(
            fund_id = fund_id
        )
        response = get_data(endpoint=url)
        if response and "id" in response:
            return Fund.from_json(response)
        
