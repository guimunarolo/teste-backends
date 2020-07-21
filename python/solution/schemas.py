import uuid
from typing import List

from pydantic import BaseModel


class Warranty(BaseModel):
    id: uuid.UUID
    proposal_id: uuid.UUID
    warranty_value: float
    warranty_province: str


class Proponent(BaseModel):
    id: uuid.UUID
    proposal_id: uuid.UUID
    proponent_name: str
    proponent_age: int
    proponent_monthly_income: float
    proponent_is_main: bool


class Proposal(BaseModel):
    id: uuid.UUID
    proposal_loan_value: float
    proposal_number_of_monthly_installments: int
    warranties: List[Warranty] = []
    proponents: List[Proponent] = []
