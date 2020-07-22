import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel


class Event(BaseModel):
    event_id: uuid.UUID
    event_schema: str
    event_action: str
    event_timestamp: datetime


class Warranty(BaseModel):
    proposal_id: uuid.UUID
    warranty_id: uuid.UUID
    warranty_value: float
    warranty_province: str

    @classmethod
    def build_from_message(cls, message):
        return cls(
            proposal_id=message[0],
            warranty_id=message[1],
            warranty_value=message[2],
            warranty_province=message[3],
        )


class Proponent(BaseModel):
    proposal_id: uuid.UUID
    proponent_id: uuid.UUID
    proponent_name: str
    proponent_age: int
    proponent_monthly_income: float
    proponent_is_main: bool

    @classmethod
    def build_from_message(cls, message):
        return cls(
            proposal_id=message[0],
            proponent_id=message[1],
            proponent_name=message[2],
            proponent_age=message[3],
            proponent_monthly_income=message[4],
            proponent_is_main=message[5],
        )


class Proposal(BaseModel):
    proposal_id: uuid.UUID
    proposal_loan_value: float
    proposal_number_of_monthly_installments: int
    warranties: List[Warranty] = []
    proponents: List[Proponent] = []

    @classmethod
    def build_from_message(cls, message):
        return cls(
            proposal_id=message[0],
            proposal_loan_value=message[1],
            proposal_number_of_monthly_installments=message[2],
        )
