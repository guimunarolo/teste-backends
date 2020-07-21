import uuid

import pytest

from solution.schemas import Proponent, Proposal, Warranty


class TestProponent:
    def test_parse(self, proponent_data):
        proponent = Proponent(**proponent_data)

        assert proponent.id == uuid.UUID(proponent_data["id"])
        assert proponent.proposal_id == uuid.UUID(proponent_data["proposal_id"])
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


class TestWarranty:
    def test_parse(self, warranty_data):
        warranty = Warranty(**warranty_data)

        assert warranty.id == uuid.UUID(warranty_data["id"])
        assert warranty.proposal_id == uuid.UUID(warranty_data["proposal_id"])
        assert warranty.warranty_value == float(warranty_data["warranty_value"])
        assert warranty.warranty_province == warranty_data["warranty_province"]


class TestProposal:
    def test_parse(self, proposal_data):
        proposal = Proposal(**proposal_data)

        assert proposal.id == uuid.UUID(proposal_data["id"])
        assert proposal.proposal_loan_value == float(proposal_data["proposal_loan_value"])
        assert proposal.warranties == []
        assert proposal.proponents == []
        expected_installments = int(proposal_data["proposal_number_of_monthly_installments"])
        assert proposal.proposal_number_of_monthly_installments == expected_installments

    def test_relateds_parse(self, proposal_data, warranty_data, proponent_data):
        proposal_data["proponents"] = [proponent_data]
        proposal_data["warranties"] = [warranty_data]
        proposal = Proposal(**proposal_data)

        assert len(proposal.warranties) == 1
        assert isinstance(proposal.warranties[0], Warranty)
        assert len(proposal.proponents) == 1
        assert isinstance(proposal.proponents[0], Proponent)
