from dataclasses import dataclass
from typing import List


@dataclass
class Account(object):
    id: str
    email: str
    applications: List[str]

    @staticmethod
    def from_json(data: dict):
        return Account(
            id=data.get("id"),
            email=data.get("email"),
            applications=data.get("applications"),
        )
