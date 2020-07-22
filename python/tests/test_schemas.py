import uuid

import pytest

from solution.schemas import Event, Proponent, Proposal, Warranty


class TesteEvent:
    def test_parse(self, event_data):
        event = Event(**event_data)

        assert event.event_id == uuid.UUID(event_data["event_id"])
        assert event.event_schema == event_data["event_schema"]
        assert event.event_action == event_data["event_action"]
        assert event.event_timestamp.isoformat().replace("+00:00", "Z") == event_data["event_timestamp"]


class TestProponent:
    def test_parse(self, proponent_data):
        proponent = Proponent(**proponent_data)

        assert proponent.proposal_id == uuid.UUID(proponent_data["proposal_id"])
        assert proponent.proponent_id == uuid.UUID(proponent_data["proponent_id"])
        assert proponent.proponent_name == proponent_data["proponent_name"]
        assert proponent.proponent_age == int(proponent_data["proponent_age"])
        assert proponent.proponent_monthly_income == float(proponent_data["proponent_monthly_income"])
        assert proponent.proponent_is_main == bool(proponent_data["proponent_is_main"])

    @pytest.mark.parametrize(
        "value, expected_result",
        (
            (0, False),
            ("False", False),
            ("false", False),
            ("FALSE", False),
            (1, True),
            ("True", True),
            ("true", True),
            ("TRUE", True),
        ),
    )
    def test_proponent_is_main_translation(self, proponent_data, value, expected_result):
        proponent_data["proponent_is_main"] = value
        proponent = Proponent(**proponent_data)

        assert proponent.proponent_is_main is expected_result

    def test_build_from_message(self, proponent_data):
        message = list(proponent_data.values())
        proponent = Proponent.build_from_message(message)

        assert proponent.proposal_id == uuid.UUID(message[0])
        assert proponent.proponent_id == uuid.UUID(message[1])
        assert proponent.proponent_name == message[2]
        assert proponent.proponent_age == int(message[3])
        assert proponent.proponent_monthly_income == float(message[4])
        assert proponent.proponent_is_main == bool(message[5])


class TestWarranty:
    def test_parse(self, warranty_data):
        warranty = Warranty(**warranty_data)

        assert warranty.warranty_id == uuid.UUID(warranty_data["warranty_id"])
        assert warranty.proposal_id == uuid.UUID(warranty_data["proposal_id"])
        assert warranty.warranty_value == float(warranty_data["warranty_value"])
        assert warranty.warranty_province == warranty_data["warranty_province"]

    def test_build_from_message(self, warranty_data):
        message = list(warranty_data.values())
        warranty = Warranty.build_from_message(message)

        assert warranty.proposal_id == uuid.UUID(message[0])
        assert warranty.warranty_id == uuid.UUID(message[1])
        assert warranty.warranty_value == float(message[2])
        assert warranty.warranty_province == message[3]


class TestProposal:
    def test_parse(self, proposal_data):
        proposal = Proposal(**proposal_data)

        assert proposal.proposal_id == uuid.UUID(proposal_data["proposal_id"])
        assert proposal.proposal_loan_value == float(proposal_data["proposal_loan_value"])
        assert proposal.warranties == {}
        assert proposal.proponents == {}
        expected_installments = int(proposal_data["proposal_number_of_monthly_installments"])
        assert proposal.proposal_number_of_monthly_installments == expected_installments

    def test_warranties_mapping(self, proposal_data, warranty_data):
        warranty = Warranty(**warranty_data)
        proposal = Proposal(**proposal_data)
        proposal.warranties[warranty.warranty_id] = warranty

        assert len(proposal.warranties) == 1
        assert proposal.warranties[warranty.warranty_id] == warranty

    def test_proponent_mapping(self, proposal_data, proponent_data):
        proponent = Proponent(**proponent_data)
        proposal = Proposal(**proposal_data)
        proposal.proponents[proponent.proponent_id] = proponent

        assert len(proposal.proponents) == 1
        assert proposal.proponents[proponent.proponent_id] == proponent

    def test_build_from_message(self, proposal_data):
        message = list(proposal_data.values())
        proposal = Proposal.build_from_message(message)

        assert proposal.proposal_id == uuid.UUID(message[0])
        assert proposal.proposal_loan_value == float(message[1])
        assert proposal.proposal_number_of_monthly_installments == int(message[2])
        assert proposal.warranties == {}
        assert proposal.proponents == {}
