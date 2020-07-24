import pytest

from solution.schemas import EventMetadata, Proponent, Proposal, Warranty


@pytest.fixture
def warranty_data():
    return {
        "proposal_id": "901557cb-01b5-4747-ad73-5d1e53d16bac",
        "warranty_id": "92139ccf-848e-4e2f-97b3-39a8851d1a87",
        "warranty_value": "4488813.77",
        "warranty_province": "GO",
    }


@pytest.fixture
def proponent_data():
    return {
        "proposal_id": "901557cb-01b5-4747-ad73-5d1e53d16bac",
        "proponent_id": "9a4f6388-f937-4da5-8293-6b2dac7d7afb",
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
        "event_schema": "foo",
        "event_action": "test",
        "event_timestamp": "2020-01-01T00:00:00Z",
    }


# events metadatas


@pytest.fixture
def proposal_created_metadata(event_data):
    event_data["event_schema"] = "proposal"
    event_data["event_action"] = "created"
    return EventMetadata(**event_data)


@pytest.fixture
def proposal_updated_metadata(event_data):
    event_data["event_schema"] = "proposal"
    event_data["event_action"] = "updated"
    return EventMetadata(**event_data)


@pytest.fixture
def proposal_deleted_metadata(event_data):
    event_data["event_schema"] = "proposal"
    event_data["event_action"] = "deleted"
    return EventMetadata(**event_data)


@pytest.fixture
def proponent_added_metadata(event_data):
    event_data["event_schema"] = "proponent"
    event_data["event_action"] = "added"
    return EventMetadata(**event_data)


@pytest.fixture
def proponent_updated_metadata(event_data):
    event_data["event_schema"] = "proponent"
    event_data["event_action"] = "updated"
    return EventMetadata(**event_data)


@pytest.fixture
def proponent_removed_metadata(event_data):
    event_data["event_schema"] = "proponent"
    event_data["event_action"] = "removed"
    return EventMetadata(**event_data)


@pytest.fixture
def warranty_added_metadata(event_data):
    event_data["event_schema"] = "warranty"
    event_data["event_action"] = "added"
    return EventMetadata(**event_data)


@pytest.fixture
def warranty_updated_metadata(event_data):
    event_data["event_schema"] = "warranty"
    event_data["event_action"] = "updated"
    return EventMetadata(**event_data)


@pytest.fixture
def warranty_removed_metadata(event_data):
    event_data["event_schema"] = "warranty"
    event_data["event_action"] = "removed"
    return EventMetadata(**event_data)


# schemas objs


@pytest.fixture
def proposal(proposal_data):
    return Proposal(**proposal_data)


@pytest.fixture
def proponent(proponent_data):
    return Proponent(**proponent_data)


@pytest.fixture
def warranty(warranty_data):
    return Warranty(**warranty_data)
