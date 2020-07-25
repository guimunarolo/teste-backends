from unittest import mock

import pytest

from solution.core import Dispatcher, read_events
from solution.schemas import EventMetadata


@pytest.fixture
def dispatcher():
    return Dispatcher()


@pytest.fixture
def raw_event():
    return "72ff1d14-756a-4549-9185-e60e326baf1b,test,testing,2020-01-01T01:02:03Z,80921e5f-4307-4623-9ddb-5bf826a31dd7,1141424.0,240"


@pytest.fixture
def event_data(raw_event):
    return {
        "event_id": "72ff1d14-756a-4549-9185-e60e326baf1b",
        "event_schema": "test",
        "event_action": "testing",
        "event_timestamp": "2020-01-01T01:02:03Z",
        "message": ["80921e5f-4307-4623-9ddb-5bf826a31dd7", "1141424.0", "240"],
    }


@pytest.mark.parametrize(
    "input_filepath, output_filepath",
    (
        ("../test/input/input000.txt", "../test/output/output000.txt"),
        ("../test/input/input001.txt", "../test/output/output001.txt"),
        ("../test/input/input002.txt", "../test/output/output002.txt"),
        ("../test/input/input003.txt", "../test/output/output003.txt"),
        ("../test/input/input004.txt", "../test/output/output004.txt"),
        ("../test/input/input005.txt", "../test/output/output005.txt"),
        ("../test/input/input006.txt", "../test/output/output006.txt"),
        ("../test/input/input007.txt", "../test/output/output007.txt"),
        ("../test/input/input008.txt", "../test/output/output008.txt"),
        # ("../test/input/input009.txt", "../test/output/output009.txt"),
        ("../test/input/input010.txt", "../test/output/output010.txt"),
        ("../test/input/input011.txt", "../test/output/output011.txt"),
        ("../test/input/input012.txt", "../test/output/output012.txt"),
    ),
)
def test_read_events_with_test_files(input_filepath, output_filepath):
    with open(input_filepath, "r") as input_file, open(output_filepath, "r") as output_file:
        assert read_events(input_file.read()) == output_file.read()


def test_dispatcher_calls_right_handler(dispatcher, raw_event, event_data):
    handle_mock = mock.Mock()
    handler_class_mock = mock.Mock()
    handler_class_mock.return_value.handle = handle_mock

    dispatcher.handlers = {"test": handler_class_mock}

    message = event_data.pop("message")
    event_metadata = EventMetadata(**event_data)

    assert dispatcher.dispatch(raw_event) is None
    assert handler_class_mock.called is True
    assert handler_class_mock.call_args == mock.call({})
    assert handle_mock.called is True
    assert handle_mock.call_args == mock.call(event_metadata, message)


def test_dispatcher_avoid_repeated_event_id(dispatcher, raw_event, event_data):
    handle_mock = mock.Mock()
    handler_class_mock = mock.Mock()
    handler_class_mock.return_value.handle = handle_mock

    dispatcher.handlers = {"test": handler_class_mock}
    dispatcher.processed_events = [event_data["event_id"]]

    assert dispatcher.dispatch(raw_event) is None
    assert handler_class_mock.called is False
    assert handle_mock.called is False


def test_dispatcher_raises_when_cant_handle_schema(dispatcher, raw_event):
    dispatcher.handlers = {}

    with pytest.raises(ValueError):
        dispatcher.dispatch(raw_event)
