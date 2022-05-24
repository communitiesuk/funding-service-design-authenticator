from dataclasses import dataclass
from typing import List

from external_data.models.round import Round


@dataclass
class Fund:
    name: str
    identifier: str
    description: str
    rounds: List[Round] = None

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("fund_name"),
            identifier=data.get("fund_id"),
            description=data.get("fund_description"),
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
