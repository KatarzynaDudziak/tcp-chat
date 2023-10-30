import pytest
import json
import struct
from unittest import mock
from unittest.mock import call, MagicMock
from client import *


@mock.patch('client.socket')
@mock.patch('client.Event')
@mock.patch('client.MessageHandler')
def test_should_create_socket(mock_message_handler, mock_event, mock_socket):
    host ='123'
    port = 123
    q  = MagicMock()
    Client(host, port, 'nickname', q)

    mock_socket.socket.assert_called_once_with(mock_socket.AF_INET, mock_socket.SOCK_STREAM)
    mock_socket.socket.return_value.settimeout.assert_called_once()
    mock_socket.socket.return_value.connect.assert_called_once_with((host, port))


@mock.patch('client.socket')
@mock.patch('client.Event')
@mock.patch('client.MessageHandler')
def test_should_send_encoded_message(mock_message_handler, mock_event, mock_socket):
    host ='123'
    port = 123
    q  = MagicMock()
    message = MagicMock()
    client = Client(host, port, 'nickname', q)

    client.write_message(message)

    client.conn.send.assert_called_once_with(message.encode.return_value)


@mock.patch('client.socket')
@mock.patch('client.Event')
@mock.patch('client.MessageHandler')
def test_should_close_connection(mock_message_handler, mock_event, mock_socket):
    host ='123'
    port = 123
    q  = MagicMock()
    conn = MagicMock()
    mock_socket.socket.return_value = conn
    client = Client(host, port, 'nickname', q)

    client.stop()

    mock_event.return_value.set.assert_called_once()
    mock_message_handler.return_value.join.assert_called_once()
    conn.close.assert_called_once()


def test_should_decode_message():
    conn = MagicMock()
    author = 'author'
    content = 'message'
    message = {'author' : author,
         'message' : content}
    json_obj = json.dumps(message)
    header = (struct.pack('!I', len(json_obj)))
    encode_message = json_obj.encode()
    conn.recv.side_effect = [header, encode_message]

    return_message = get_message(conn)

    assert return_message == json_obj


def test_should_raise_connection_aborted_error_when_empty_header():
    conn = MagicMock()
    conn.recv.return_value = b''

    with pytest.raises(Exception) as ex:
        get_message(conn)
    
    assert ex.type == ConnectionAbortedError


@mock.patch('client.get_message')
@mock.patch('client.Message')
@mock.patch('client.Event')
@mock.patch('client.Thread')
def test_should_put_received_message_on_queue(mock_thread, mock_event, mock_message, mock_get_message):
    conn = MagicMock()
    q = MagicMock()
    nickname = MagicMock()
    event = MagicMock()
    mock_get_message.return_value = 'messsage'
    message_handler = MessageHandler(conn, q, nickname, event)
    event.is_set.side_effect = [False, True]

    message_handler.run()

    q.put.assert_called_once_with(mock_message.return_value)


@mock.patch('client.get_message')
@mock.patch('client.Message')
@mock.patch('client.Event')
@mock.patch('client.Thread')
def test_should_send_received_nick_message(mock_thread, mock_event, mock_message, mock_get_message):
    conn = MagicMock()
    q = MagicMock()
    nickname = MagicMock()
    event = MagicMock()
    mock_get_message.return_value = 'nick'
    message_handler = MessageHandler(conn, q, nickname, event)
    event.is_set.side_effect = [False, True]

    message_handler.run()

    conn.send.assert_called_once_with(nickname.encode.return_value)
    conn.close.assert_called_once()


@mock.patch('client.get_message')
@mock.patch('client.Message')
@mock.patch('client.Event')
@mock.patch('client.Thread')
def test_should_back_to_while_loop_when_no_message(mock_thread, mock_event, mock_message, mock_get_message):
    conn = MagicMock()
    q = MagicMock()
    nickname = MagicMock()
    event = MagicMock()
    mock_get_message.return_value = None
    expected_calls = [(call(), call())]
    message_handler = MessageHandler(conn, q, nickname, event)
    event.is_set.side_effect = [False, True]

    message_handler.run()

    q.put.assert_not_called()
    event.is_set.assert_has_calls(expected_calls)


@mock.patch('client.get_message')
@mock.patch('client.Message')
@mock.patch('client.Event')
@mock.patch('client.Thread')
def test_should_catch__errors_after_disconnected(mock_thread, mock_event, mock_message, mock_get_message):
    conn = MagicMock()
    q = MagicMock()
    nickname = MagicMock()
    event = MagicMock()
    mock_get_message.side_effect = [ConnectionAbortedError, TimeoutError]
    message_handler = MessageHandler(conn, q, nickname, event)
    event.is_set.side_effect = [False, False, True]

    message_handler.run()
    
    q.put.assert_called_once_with(mock_message.return_value)
