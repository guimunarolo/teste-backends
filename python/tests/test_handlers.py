import uuid
from unittest import mock

import pytest

from solution import stored_proposals
from solution.exceptions import ReferenceDoesNotExist
from solution.handlers import BaseHandler, ProponentHandler, ProposalHandler, WarrantyHandler
from solution.schemas import EventMetadata, Proposal


class TestBaseHandler:
    def test_get_stored_proposal(self, proposal):
        proposal_id = proposal.proposal_id
        stored_proposals.update({proposal_id: proposal})

        assert BaseHandler()._get_stored_proposal(proposal_id) is proposal

    def test_get_stored_proposal_raises_exception(self, proposal):
        proposal_id = proposal.proposal_id
        stored_proposals.pop(proposal_id, None)

        with pytest.raises(ReferenceDoesNotExist):
            BaseHandler()._get_stored_proposal(proposal_id)

    def test_build_action_kwargs_with_deleted_action(self, event_data):
        event_data["event_schema"] = "foo"
        event_data["event_action"] = "deleted"
        metadata = EventMetadata(**event_data)
        some_id = uuid.uuid4()
        message = [str(some_id)]

        expected_result = {"metadata": metadata, "foo_id": some_id}
        assert BaseHandler()._build_action_kwargs(metadata, message) == expected_result

    def test_build_action_kwargs_with_removed_action(self, event_data):
        event_data["event_schema"] = "foo"
        event_data["event_action"] = "removed"
        metadata = EventMetadata(**event_data)
        some_id = uuid.uuid4()
        some_other_id = uuid.uuid4()
        message = [str(some_id), str(some_other_id)]

        expected_result = {"metadata": metadata, "parent_id": some_id, "foo_id": some_other_id}
        assert BaseHandler()._build_action_kwargs(metadata, message) == expected_result

    @pytest.mark.parametrize("common_action", ("created", "added", "updated"))
    def test_build_action_kwargs_with_common_action(self, common_action, event_data, proposal_data):
        event_data["event_schema"] = "foo"
        event_data["event_action"] = common_action
        metadata = EventMetadata(**event_data)
        message = list(proposal_data.values())
        BaseHandler.schema_class = Proposal

        expected_result = {"metadata": metadata, "foo": Proposal(**proposal_data)}
        assert BaseHandler()._build_action_kwargs(metadata, message) == expected_result

    def test_handle_calls_processor(self, event_data):
        event_data["event_action"] = "created"
        metadata = EventMetadata(**event_data)
        base_handler = BaseHandler()
        base_handler.process_created = mock.Mock(return_value=None)
        base_handler._build_action_kwargs = mock.Mock(return_value={"metadata": metadata, "foo": None})

        assert base_handler.handle(metadata, message={}) is None
        assert base_handler.process_created.called is True
        assert base_handler._build_action_kwargs.called is True

    def test_handle_raises_not_implemented_whith_uncovered_event_action(self, event_data):
        event_data["event_action"] = "uncovered"
        metadata = EventMetadata(**event_data)
        base_handler = BaseHandler()
        base_handler._build_action_kwargs = mock.Mock(return_value={"metadata": metadata, "foo": None})

        with pytest.raises(NotImplementedError):
            base_handler.handle(metadata, message={})
            assert base_handler._build_action_kwargs.called is False


class TestProposalHandler:
    handler = ProposalHandler()

    def test_process_created_stores_proposal(self, proposal_created_metadata, proposal):
        # avoid tests randomization problems
        stored_proposals.pop(proposal.proposal_id, None)

        assert self.handler.process_created(proposal_created_metadata, proposal) is None
        assert stored_proposals.get(proposal.proposal_id) == proposal

    def test_process_created_idempotency(self, proposal_created_metadata, proposal):
        stored_proposals[proposal.proposal_id] = proposal

        assert self.handler.process_created(proposal_created_metadata, proposal) is None
        assert stored_proposals.get(proposal.proposal_id) == proposal

    def test_process_updated_updates_proposal_without_loses_relateds(
        self, proposal_updated_metadata, proposal, proponent, warranty, proposal_data
    ):
        # store proposal with relateds
        proposal.proponents = {proponent.proponent_id: proponent}
        proposal.warranties = {warranty.warranty_id: warranty}
        stored_proposals[proposal.proposal_id] = proposal

        # create non stored new proposal instance
        updated_proposal = Proposal(**proposal_data)
        updated_proposal.proposal_number_of_monthly_installments = 999

        assert self.handler.process_updated(proposal_updated_metadata, updated_proposal) is None
        current_stored_proposal = stored_proposals.get(proposal.proposal_id)
        assert current_stored_proposal.proposal_number_of_monthly_installments == 999
        assert len(current_stored_proposal.proponents) == 1
        assert len(current_stored_proposal.warranties) == 1

    def test_process_updated_with_nonexistent_proposal(self, proposal_updated_metadata, proposal):
        stored_proposals.pop(proposal.proposal_id, None)

        assert self.handler.process_updated(proposal_updated_metadata, proposal) is None
        assert stored_proposals.get(proposal.proposal_id, None) is None

    def test_process_deleted(self, proposal_deleted_metadata, proposal):
        stored_proposals[proposal.proposal_id] = proposal

        assert self.handler.process_deleted(proposal_deleted_metadata, proposal.proposal_id) is None
        assert stored_proposals.get(proposal.proposal_id, None) is None


class TestProponentHandler:
    handler = ProponentHandler()

    def test_process_added_stores_proponent_in_proposal(self, proponent_added_metadata, proposal, proponent):
        stored_proposals.update({proposal.proposal_id: proposal})

        assert self.handler.process_added(proponent_added_metadata, proponent) is None
        assert proposal.proponents.get(proponent.proponent_id) is proponent

    def test_process_added_idempotency(self, proponent_added_metadata, proposal, proponent):
        # store obj to proponent id
        proposal.proponents = {proponent.proponent_id: {"test": 123}}
        stored_proposals.update({proposal.proposal_id: proposal})

        assert self.handler.process_added(proponent_added_metadata, proponent) is None
        assert proposal.proponents.get(proponent.proponent_id) == {"test": 123}

    def test_process_updated(self, proponent_updated_metadata, proposal, proponent):
        # store obj to proponent id
        proposal.proponents = {proponent.proponent_id: {"test": 123}}
        stored_proposals.update({proposal.proposal_id: proposal})

        assert self.handler.process_updated(proponent_updated_metadata, proponent) is None
        assert proposal.proponents.get(proponent.proponent_id) is proponent

    def test_process_removed(self, proponent_removed_metadata, proposal, proponent):
        proposal_id = proposal.proposal_id
        proponent_id = proponent.proponent_id
        proposal.proponents = {proponent_id: proponent}
        stored_proposals.update({proposal_id: proposal})

        assert len(proposal.proponents) == 1
        assert self.handler.process_removed(proponent_removed_metadata, proposal_id, proponent_id) is None
        assert len(proposal.proponents) == 0


class TestWarrantyHandler:
    handler = WarrantyHandler()

    def test_process_added_stores_warranty_in_proposal(self, warranty_added_metadata, proposal, warranty):
        stored_proposals.update({proposal.proposal_id: proposal})

        assert self.handler.process_added(warranty_added_metadata, warranty) is None
        assert proposal.warranties.get(warranty.warranty_id) is warranty

    def test_process_added_idempotency(self, warranty_added_metadata, proposal, warranty):
        # store obj to warranty id
        proposal.warranties = {warranty.warranty_id: {"test": 123}}
        stored_proposals.update({proposal.proposal_id: proposal})

        assert self.handler.process_added(warranty_added_metadata, warranty) is None
        assert proposal.warranties.get(warranty.warranty_id) == {"test": 123}

    def test_process_updated(self, warranty_updated_metadata, proposal, warranty):
        # store obj to warranty id
        proposal.warranties = {warranty.warranty_id: {"test": 123}}
        stored_proposals.update({proposal.proposal_id: proposal})

        assert self.handler.process_updated(warranty_updated_metadata, warranty) is None
        assert proposal.warranties.get(warranty.warranty_id) is warranty

    def test_process_removed(self, warranty_removed_metadata, proposal, warranty):
        proposal_id = proposal.proposal_id
        warranty_id = warranty.warranty_id
        proposal.warranties = {warranty_id: warranty}
        stored_proposals.update({proposal_id: proposal})

        assert len(proposal.warranties) == 1
        assert self.handler.process_removed(warranty_removed_metadata, proposal_id, warranty_id) is None
        assert len(proposal.warranties) == 0
