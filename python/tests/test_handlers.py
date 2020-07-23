import uuid
from unittest import mock

import pytest

from solution import stored_proposals
from solution.handlers import BaseHandler, ProposalHandler
from solution.schemas import EventMetadata, Proposal


class TestBaseHandler:
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
