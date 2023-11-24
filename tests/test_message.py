from unittest.mock import MagicMock
from message import *


def test_should_convert_to_dict():
    message = Message()
    obj_json = '{"publication_date": "date", "author": "test", "message": "message", "type": 1}'

    message.convert_to_obj(obj_json)

    assert message.publication_date == 'date'
    assert message.author == 'test'
    assert message.message == 'message'
    assert message.type == Type.USER


def test_should_return_encoded_message(mocker):
    mock_datetime = mocker.patch('message.datetime')
    mock_struct = mocker.patch('message.struct')
    mock_json = mocker.patch('message.json')
    converted_message_mock = MagicMock()
    header_mock = MagicMock()
    mock_datetime.now.return_value.strftime.return_value = 'date'
    mock_json.dumps.return_value = converted_message_mock
    converted_message_mock.__len__.return_value = 2
    mock_struct.pack.return_value = header_mock
    message = Message()
    message.author = 'test'
    message.message = 'message'
    message.type = Type.USER
    
    encoded_message = message.encode_message()

    converted_message_mock.__len__.assert_called_once()
    mock_struct.pack.assert_called_once_with('!I', 2)
    header_mock.__add__.assert_called_once_with(converted_message_mock.encode.return_value)
    assert encoded_message == header_mock.__add__(converted_message_mock.encode.return_value)


def test_should_return_encoded_nickname(mocker):
    mock_datetime = mocker.patch('message.datetime')
    mock_struct = mocker.patch('message.struct')
    mock_datetime.now.return_value.strftime.return_value = 'date'
    header_mock = MagicMock()
    mock_struct.pack.return_value = header_mock
    message = Message()
    message.author = 'test'
    message.message = 'message'
    message.type = Type.USER

    encoded_nickname = message.encode_nickname(Message.NICK)

    mock_struct.pack.assert_called_once_with('!I', 4)
    header_mock.__add__.assert_called_once_with(Message.NICK.encode())
    assert encoded_nickname == header_mock.__add__(Message.NICK.encode())
