import pytest


@pytest.fixture
def warranty_data():
    return {
        "id": "92139ccf-848e-4e2f-97b3-39a8851d1a87",
        "proposal_id": "901557cb-01b5-4747-ad73-5d1e53d16bac",
        "warranty_value": "4488813.77",
        "warranty_province": "GO",
    }


@pytest.fixture
def proponent_data():
    return {
        "id": "9a4f6388-f937-4da5-8293-6b2dac7d7afb",
        "proposal_id": "901557cb-01b5-4747-ad73-5d1e53d16bac",
        "proponent_name": "Page Breitenberg",
        "proponent_age": "35",
        "proponent_monthly_income": "126096.68",
        "proponent_is_main": "true",
    }


@pytest.fixture
def proposal_data():
    return {
        "id": "901557cb-01b5-4747-ad73-5d1e53d16bac",
        "proposal_loan_value": "1656233.0",
        "proposal_number_of_monthly_installments": "108",
    }
