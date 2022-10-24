import pytest
from unittest import mock
from unittest.mock import MagicMock
from server import *


@mock.patch('server.socket.socket')
def test_create_socket(mock_socket):
    host = '123'
    port = 123
    s = create_socket(host, port)
    assert s == mock_socket.return_value


@mock.patch('server.socket.socket')
def test_socket_bind(mock_socket):
    host = '123'
    port = 123
    create_socket(host, port)
    mock_socket.return_value.bind.assert_called_once_with((host, port))


@mock.patch('server.socket.socket')
def test_socket_listen(mock_socket):
    host = '123'
    port = 123
    create_socket(host, port)
    mock_socket.return_value.listen.assert_called_once()


def test_socket_accept():
    mock_socket = MagicMock()
    mock_clients = MagicMock()
    mock_conn = MagicMock()
    mock_socket.accept.return_value = (mock_conn, 'addr')
    accept_client(mock_socket, mock_clients)
    mock_socket.accept.assert_called_once()


def test_send_nick_message():
    mock_socket = MagicMock()
    mock_clients = MagicMock()
    mock_conn = MagicMock()
    mock_socket.accept.return_value = (mock_conn, 'addr')
    accept_client(mock_socket, mock_clients)
    mock_conn.send.assert_called_once_with('nick'.encode())


def test_recv_and_decoding_nickname():
    mock_socket = MagicMock()
    mock_clients = MagicMock()
    mock_conn = MagicMock()
    mock_socket.accept.return_value = (mock_conn, 'addr')
    accept_client(mock_socket, mock_clients)
    mock_conn.recv.assert_called_once_with(1024)
    mock_conn.recv.return_value.decode.assert_called_once()


def test_adding_client_with_nickname():
    mock_socket = MagicMock()
    clients = dict()
    mock_conn = MagicMock()
    mock_socket.accept.return_value = (mock_conn, 'addr')
    mock_conn.recv.return_value.decode.return_value = 'nick'
    accept_client(mock_socket, clients)
    assert clients['addr'] == (mock_conn, 'nick')

