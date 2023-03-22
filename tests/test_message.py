import pytest
from unittest import mock
from unittest.mock import MagicMock
from message import Message, Type
import json


@mock.patch('message.datetime')
def test_convert_to_json(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = 'date'
    message = Message()
    message.author = 'test'
    message.message = 'message'
    message.type = Type.USER
    expected_json = '{"publication_date": "date", "author": "test", "message": "message", "type": 1}'

    json_obj = message.convert_to_str()
    
    assert expected_json == json_obj


def test_convert_to_dict():
    message = Message()
    expected_json = '{"publication_date": "date", "author": "test", "message": "message", "type": 1}'

    message.convert_to_obj(expected_json)

    assert message.publication_date == 'date'
    assert message.author == 'test'
    assert message.message == 'message'
    assert message.type == Type.USER

