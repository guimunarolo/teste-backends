import uuid
from unittest import mock

import pytest

from solution.exceptions import ReferenceDoesNotExist
from solution.handlers import BaseHandler, ProponentHandler, ProposalHandler, WarrantyHandler
from solution.schemas import EventMetadata, Proposal


@pytest.fixture
def base_handler():
    return BaseHandler(stored_proposals={})


@pytest.fixture
def proponent_handler():
    return ProponentHandler(stored_proposals={})


@pytest.fixture
def proposal_handler():
    return ProposalHandler(stored_proposals={})


@pytest.fixture
def warranty_handler():
    return WarrantyHandler(stored_proposals={})


class TestBaseHandler:
    def test_get_stored_proposal(self, proposal, base_handler):
        proposal_id = proposal.proposal_id
        base_handler.stored_proposals.update({proposal_id: proposal})

        assert base_handler._get_stored_proposal(proposal_id) is proposal

    def test_get_stored_proposal_raises_exception(self, proposal, base_handler):
        proposal_id = proposal.proposal_id

        with pytest.raises(ReferenceDoesNotExist):
            base_handler._get_stored_proposal(proposal_id)

    def test_build_action_kwargs_with_deleted_action(self, event_data, base_handler):
        event_data["event_schema"] = "foo"
        event_data["event_action"] = "deleted"
        metadata = EventMetadata(**event_data)
        some_id = uuid.uuid4()
        message = [str(some_id)]

        expected_result = {"metadata": metadata, "foo_id": some_id}
        assert base_handler._build_action_kwargs(metadata, message) == expected_result

    def test_build_action_kwargs_with_removed_action(self, event_data, base_handler):
        event_data["event_schema"] = "foo"
        event_data["event_action"] = "removed"
        metadata = EventMetadata(**event_data)
        some_id = uuid.uuid4()
        some_other_id = uuid.uuid4()
        message = [str(some_id), str(some_other_id)]

        expected_result = {"metadata": metadata, "parent_id": some_id, "foo_id": some_other_id}
        assert base_handler._build_action_kwargs(metadata, message) == expected_result

    @pytest.mark.parametrize("common_action", ("created", "added", "updated"))
    def test_build_action_kwargs_with_common_action(
        self, common_action, event_data, proposal_data, base_handler
    ):
        event_data["event_schema"] = "foo"
        event_data["event_action"] = common_action
        metadata = EventMetadata(**event_data)
        message = list(proposal_data.values())
        base_handler.schema_class = Proposal

        expected_result = {"metadata": metadata, "foo": Proposal(**proposal_data)}
        assert base_handler._build_action_kwargs(metadata, message) == expected_result

    def test_handle_calls_processor(self, event_data, base_handler):
        event_data["event_action"] = "created"
        metadata = EventMetadata(**event_data)
        base_handler.process_created = mock.Mock(return_value=None)
        base_handler._build_action_kwargs = mock.Mock(return_value={"metadata": metadata, "foo": None})

        assert base_handler.handle(metadata, message={}) is None
        assert base_handler.process_created.called is True
        assert base_handler._build_action_kwargs.called is True

    def test_handle_raises_not_implemented_whith_uncovered_event_action(self, event_data, base_handler):
        event_data["event_action"] = "uncovered"
        metadata = EventMetadata(**event_data)
        base_handler._build_action_kwargs = mock.Mock(return_value={"metadata": metadata, "foo": None})

        with pytest.raises(NotImplementedError):
            base_handler.handle(metadata, message={})
            assert base_handler._build_action_kwargs.called is False


class TestProposalHandler:
    def test_process_created_stores_proposal(self, proposal_created_metadata, proposal, proposal_handler):
        assert proposal_handler.process_created(proposal_created_metadata, proposal) is None
        assert proposal_handler.stored_proposals.get(proposal.proposal_id) is proposal

    def test_process_created_idempotency(self, proposal_created_metadata, proposal, proposal_handler):
        proposal_handler.stored_proposals[proposal.proposal_id] = proposal

        assert proposal_handler.process_created(proposal_created_metadata, proposal) is None
        assert proposal_handler.stored_proposals.get(proposal.proposal_id) is proposal

    def test_process_updated_updates_proposal_without_loses_related(
        self, proposal_updated_metadata, proposal, proponent, warranty, proposal_data, proposal_handler
    ):
        # store proposal with relateds
        proposal.proponents = {proponent.proponent_id: proponent}
        proposal.warranties = {warranty.warranty_id: warranty}
        proposal_handler.stored_proposals[proposal.proposal_id] = proposal

        # create non stored new proposal instance
        updated_proposal = Proposal(**proposal_data)
        updated_proposal.proposal_number_of_monthly_installments = 999

        assert proposal_handler.process_updated(proposal_updated_metadata, updated_proposal) is None
        current_stored_proposal = proposal_handler.stored_proposals.get(proposal.proposal_id)
        assert current_stored_proposal.proposal_number_of_monthly_installments == 999
        assert len(current_stored_proposal.proponents) == 1
        assert len(current_stored_proposal.warranties) == 1

    def test_process_updated_with_nonexistent_proposal(
        self, proposal_updated_metadata, proposal, proposal_handler
    ):
        assert proposal_handler.process_updated(proposal_updated_metadata, proposal) is None
        assert proposal_handler.stored_proposals.get(proposal.proposal_id, None) is None

    def test_process_deleted(self, proposal_deleted_metadata, proposal, proposal_handler):
        proposal_handler.stored_proposals[proposal.proposal_id] = proposal

        assert proposal_handler.process_deleted(proposal_deleted_metadata, proposal.proposal_id) is None
        assert proposal_handler.stored_proposals.get(proposal.proposal_id, None) is None


class TestProponentHandler:
    def test_process_added_stores_proponent_in_proposal(
        self, proponent_added_metadata, proposal, proponent, proponent_handler
    ):
        proponent_handler.stored_proposals.update({proposal.proposal_id: proposal})

        assert proponent_handler.process_added(proponent_added_metadata, proponent) is None
        assert proposal.proponents.get(proponent.proponent_id) is proponent

    def test_process_added_idempotency(
        self, proponent_added_metadata, proposal, proponent, proponent_handler
    ):
        # store obj to proponent id
        proposal.proponents = {proponent.proponent_id: {"test": 123}}
        proponent_handler.stored_proposals.update({proposal.proposal_id: proposal})

        assert proponent_handler.process_added(proponent_added_metadata, proponent) is None
        assert proposal.proponents.get(proponent.proponent_id) == {"test": 123}

    def test_process_updated(self, proponent_updated_metadata, proposal, proponent, proponent_handler):
        # store obj to proponent id
        proposal.proponents = {proponent.proponent_id: {"test": 123}}
        proponent_handler.stored_proposals.update({proposal.proposal_id: proposal})

        assert proponent_handler.process_updated(proponent_updated_metadata, proponent) is None
        assert proposal.proponents.get(proponent.proponent_id) is proponent

    def test_process_removed(self, proponent_removed_metadata, proposal, proponent, proponent_handler):
        proposal_id = proposal.proposal_id
        proponent_id = proponent.proponent_id
        proposal.proponents = {proponent_id: proponent}
        proponent_handler.stored_proposals.update({proposal_id: proposal})

        assert len(proposal.proponents) == 1
        assert (
            proponent_handler.process_removed(proponent_removed_metadata, proposal_id, proponent_id) is None
        )
        assert len(proposal.proponents) == 0


class TestWarrantyHandler:
    def test_process_added_stores_warranty_in_proposal(
        self, warranty_added_metadata, proposal, warranty, warranty_handler
    ):
        warranty_handler.stored_proposals.update({proposal.proposal_id: proposal})

        assert warranty_handler.process_added(warranty_added_metadata, warranty) is None
        assert proposal.warranties.get(warranty.warranty_id) is warranty

    def test_process_added_idempotency(self, warranty_added_metadata, proposal, warranty, warranty_handler):
        # store obj to warranty id
        proposal.warranties = {warranty.warranty_id: {"test": 123}}
        warranty_handler.stored_proposals.update({proposal.proposal_id: proposal})

        assert warranty_handler.process_added(warranty_added_metadata, warranty) is None
        assert proposal.warranties.get(warranty.warranty_id) == {"test": 123}

    def test_process_updated(self, warranty_updated_metadata, proposal, warranty, warranty_handler):
        # store obj to warranty id
        proposal.warranties = {warranty.warranty_id: {"test": 123}}
        warranty_handler.stored_proposals.update({proposal.proposal_id: proposal})

        assert warranty_handler.process_updated(warranty_updated_metadata, warranty) is None
        assert proposal.warranties.get(warranty.warranty_id) is warranty

    def test_process_removed(self, warranty_removed_metadata, proposal, warranty, warranty_handler):
        proposal_id = proposal.proposal_id
        warranty_id = warranty.warranty_id
        proposal.warranties = {warranty_id: warranty}
        warranty_handler.stored_proposals.update({proposal_id: proposal})

        assert len(proposal.warranties) == 1
        assert warranty_handler.process_removed(warranty_removed_metadata, proposal_id, warranty_id) is None
        assert len(proposal.warranties) == 0
