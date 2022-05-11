from dataclasses import dataclass
from typing import List

from api.session.models.application import Application


@dataclass
class Account(object):
    id: str
    email: str
    applications: List[Application]

    @staticmethod
    def from_json(data: dict):
        return Account(
            id=data.get("id"),
            email=data.get("email"),
            applications=data.get("applications"),
        )
