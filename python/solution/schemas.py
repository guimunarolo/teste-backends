import uuid
from datetime import datetime
from typing import Mapping

from pydantic import BaseModel

from .validations import (
    has_main_proponent_with_valid_monthly_income,
    has_proponents_with_valid_age,
    has_valid_loan_installments_number,
    has_valid_loan_value,
    has_valid_main_proponents_number,
    has_valid_proponents_number,
    has_valid_warranties_number_and_valid_warranted_value,
)


class EventMetadata(BaseModel):
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
    warranties: Mapping[uuid.UUID, Warranty] = {}
    proponents: Mapping[uuid.UUID, Proponent] = {}

    @classmethod
    def build_from_message(cls, message):
        return cls(
            proposal_id=message[0],
            proposal_loan_value=message[1],
            proposal_number_of_monthly_installments=message[2],
        )

    def get_validations(self):
        return (
            has_valid_loan_value,
            has_valid_loan_installments_number,
            has_valid_proponents_number,
            has_valid_main_proponents_number,
            has_proponents_with_valid_age,
            has_valid_warranties_number_and_valid_warranted_value,
            has_main_proponent_with_valid_monthly_income,
        )

    def is_valid(self):
        for validate in self.get_validations():
            if not validate(proposal=self):
                return False

        return True
