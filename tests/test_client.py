import pytest
from unittest import mock
from unittest.mock import MagicMock
from client import *


@pytest.fixture
def client():
    client = MagicMock()
    return client


@mock.patch('client.socket.socket')
def test_create_client(mock_socket):
    host = '123'
    port = 123
    client = create_client(host, port)
    assert client == mock_socket.return_value


@mock.patch('client.handle_recv_message')
def test_recv_message(mock_handle_recv_message, client):
    mock_handle_recv_message.side_effect = Exception
    receive_message('nickname', client)
    client.close.assert_called_once()


def test_catch_exception_in_handle_message(client):
    client.recv.return_value.decode.return_value = False
    with pytest.raises(Exception):
        handle_recv_message(client, 'nickname')


def test_handle_nick_message(client):
    client.recv.return_value.decode.return_value = 'nick'
    handle_recv_message(client, 'nickname')
    client.send.assert_called_once_with('nickname'.encode())


@mock.patch('client.print')
def test_handle_correct_message(mock_print, client):
    client.recv.return_value.decode.return_value = 'message'
    handle_recv_message(client, 'nickname')
    mock_print.assert_called_once_with('message')


@mock.patch('client.send_message_to_server')
def test_catch_exception_in_write_message(mock_send_message_to_server, client):
    mock_send_message_to_server.side_effect = Exception
    write_message(client, 'nickname')
    client.close.assert_called_once()


@mock.patch('client.input')
def test_send_correct_message_to_server(mock_input, client):
    mock_input.return_value = 'message'
    message = 'nickname: message'
    send_message_to_server(client, 'nickname')
    client.send.assert_called_once_with(message.encode())


@mock.patch('client.write_message')
@mock.patch('client.Thread')
@mock.patch('client.create_client')
@mock.patch('client.input')
def test_main(mock_input, mock_create_client, mock_Thread, mock_write_message):
    mock_input.return_value = 'nickname'
    mock_create_client.return_value = 'client'
    main()
    mock_create_client.assert_called_once_with('127.0.0.1', 3888)
    mock_Thread.return_value.start.assert_called_once()
    mock_write_message.assert_called_once_with('client', 'nickname')
