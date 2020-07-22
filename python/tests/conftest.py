import pytest


@pytest.fixture
def warranty_data():
    return {
        "warranty_id": "92139ccf-848e-4e2f-97b3-39a8851d1a87",
        "proposal_id": "901557cb-01b5-4747-ad73-5d1e53d16bac",
        "warranty_value": "4488813.77",
        "warranty_province": "GO",
    }


@pytest.fixture
def proponent_data():
    return {
        "proponent_id": "9a4f6388-f937-4da5-8293-6b2dac7d7afb",
        "proposal_id": "901557cb-01b5-4747-ad73-5d1e53d16bac",
        "proponent_name": "Page Breitenberg",
        "proponent_age": "35",
        "proponent_monthly_income": "126096.68",
        "proponent_is_main": "true",
    }


@pytest.fixture
def proposal_data():
    return {
        "proposal_id": "901557cb-01b5-4747-ad73-5d1e53d16bac",
        "proposal_loan_value": "1656233.0",
        "proposal_number_of_monthly_installments": "108",
    }


@pytest.fixture
def event_data():
    return {
        "event_id": "b0f68661-3937-4b94-8cb8-b7f5878f368e",
        "event_schema": "proposal",
        "event_action": "created",
        "event_timestamp": "2019-11-11T14:29:16Z",
    }
