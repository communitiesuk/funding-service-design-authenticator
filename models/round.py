from dataclasses import dataclass
from datetime import datetime


@dataclass
class Round:
    title: str
    identifier: str
    fund_id: str
    opens: datetime
    deadline: datetime
    assessment_deadline: datetime
    eligibility_criteria: dict

    @staticmethod
    def from_json(data: dict):
        eligibility_criteria = {}
        if "eligibility_criteria" in data:
            for key, value in data["eligibility_criteria"].items():
                eligibility_criteria.update({key: value})
        return Round(
            title=data.get("round_title"),
            identifier=data.get("round_id"),
            fund_id=data.get("fund_id"),
            opens=data.get("opens"),
            deadline=data.get("deadline"),
            assessment_deadline=data.get("deadline"),
            eligibility_criteria=eligibility_criteria,
        )

    def add_eligibility_criteria(self, key: str, value: object):
        self.eligibility_criteria.update({key: value})
