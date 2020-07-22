from unittest import mock

import pytest

from solution.handlers import BaseHandler


@pytest.fixture
def base_handler():
    handler = BaseHandler()
    handler._build_parsed_message = mock.Mock(return_value={})
    handler._get_message_argument_name = mock.Mock(return_value="test")
    handler.process_test = mock.Mock(return_value=True)
    return handler


class TestBaseHandler:
    def test_handle_calls_processor_with_params(self, base_handler, event_data):
        assert base_handler.handle(event=event_data, message={}) is True
        base_handler.process_test.assert_called_once_with(event=event_data, test={})

    def test_handle_raises_not_implemented_whith_uncovered_event_action(self, base_handler, event_data):
        event_data["event_action"] = "uncovered"

        with pytest.raises(NotImplementedError):
            base_handler.handle(event=event_data, message={})
