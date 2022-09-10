from __future__ import annotations

import inspect
from dataclasses import dataclass


@dataclass
class ContactDetails:
    phone: str
    email_address: str
    text_phone: str

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )


@dataclass
class SupportAvailability:
    time: str
    days: str

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )


@dataclass
class Round:
    id: str
    assessment_criteria_weighting: list
    assessment_deadline: str
    deadline: str
    fund_id: str
    opens: str
    title: str
    contact_details: ContactDetails
    support_availability: SupportAvailability

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )
