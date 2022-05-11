from dataclasses import dataclass


@dataclass
class Application(object):
    id: str

    @staticmethod
    def from_json(data: dict):
        return Application(
            id=data.get("id"),
        )
