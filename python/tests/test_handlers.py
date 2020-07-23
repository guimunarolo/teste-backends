import uuid
from unittest import mock

import pytest

from solution.handlers import BaseHandler
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
