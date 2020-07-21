from unittest import mock

import pytest

from solution.handlers import BaseHandler


class TestBaseHandler:
    def test_handle(self, event_data):
        handler = BaseHandler()
        handler.schema_class = mock.Mock(__name__="Foo", return_value={})
        handler.process = mock.Mock()

        assert handler.handle(event=event_data, message={}) is None
        handler.process.assert_called_once_with(event=event_data, foo={})

    def test_process(self, event_data):
        handler = BaseHandler()

        with pytest.raises(NotImplementedError):
            handler.process(event=event_data, foo={})
