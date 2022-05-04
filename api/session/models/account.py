from dataclasses import dataclass


@dataclass
class Account(object):
    id: str
    email: str

    @staticmethod
    def from_json(data: dict):
        return Account(
            id=data.get("id"),
            email=data.get("email"),
        )
