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


@mock.patch('server.Thread')
@mock.patch('server.accept_client')
def test_handle_one_client(mock_accept_client, mock_Thread):
    mock_socket = MagicMock()
    mock_clients = MagicMock()
    handle_one_client(mock_socket, mock_clients)
    mock_accept_client.assert_called_once_with(mock_socket, mock_clients)
    mock_Thread.return_value.start.assert_called_once


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


def test_returning_addr():
    mock_socket = MagicMock()
    clients = dict()
    mock_conn = MagicMock()
    mock_socket.accept.return_value = (mock_conn, 'addr')
    assert accept_client(mock_socket, clients) == 'addr'


@mock.patch('server.get_connection')
@mock.patch('server.get_nickname')
def test_send_server_message(mock_get_nickname, mock_get_connection):
    mock_clients = MagicMock()
    addr = 'addr'
    mock_get_nickname.return_value = 'nick'
    send_server_messages_on_client_join(mock_clients, addr)
    message = 'Hello nick from server to client'
    mock_get_connection.return_value.send.assert_called_once_with(message.encode())


def test_returning_nickname():
    clients = {'addr' : ('conn', 'nickname')}
    assert get_nickname(clients, 'addr') == 'nickname'


def test_no_nickname_in_clients():
    clients = {'addr' : 'conn'}
    with pytest.raises(KeyError):
        get_nickname(clients, 'addr2')


def test_returning_connection():
    clients = {'addr' : ('conn', 'nickname')}
    assert get_connection(clients, 'addr') == 'conn'


def test_no_connection_in_clients():
    clients = {'addr' : 'nickname'}
    with pytest.raises(KeyError):
        get_connection(clients, 'addr2')


@mock.patch('server.handle_messages_for_client')
def test_no_handle_messages_for_no_clients(mock_handle_messages_for_client):
    clients = {}
    handle_messages(clients, 'addr')
    mock_handle_messages_for_client.assert_not_called


@mock.patch('server.handle_messages_for_client')
@mock.patch('server.len')
def test_handle_messages_one_clients(mock_len, mock_handle_messages_for_client):
    mock_clients = MagicMock()
    mock_len.side_effect = [1, 0]
    handle_messages(mock_clients, 'addr')
    mock_handle_messages_for_client.assert_called_once


@mock.patch('server.handle_received_data')
@mock.patch('server.get_connection')
@mock.patch('server.get_nickname')
def test_handle_messages_for_client(mock_get_nickname, mock_get_connection, mock_handle_received_data):
    mock_clients = MagicMock()
    handle_messages_for_client(mock_clients, 'addr')
    mock_get_nickname.assert_called_once_with(mock_clients, 'addr')
    nickname = mock_get_nickname.return_value
    mock_get_connection.assert_called_once_with(mock_clients, 'addr')
    conn = mock_get_connection.return_value
    mock_handle_received_data.assert_called_once_with(mock_clients, 'addr', nickname, conn)


def test_recv_valid_data():
    mock_conn = MagicMock()
    mock_clients = MagicMock()
    handle_received_data(mock_clients, 'addr', 'nickname', mock_conn)
    mock_conn.recv.assert_called_once_with(1024)
    mock_conn.recv.return_value.decode.assert_called_once()


@mock.patch('server.broadcast')
def test_run_broadcast_if_valid_data(mock_broadcast):
    mock_conn = MagicMock()
    mock_clients = MagicMock()
    handle_received_data(mock_clients, 'addr', 'nickname', mock_conn)
    mock_conn.recv.assert_called_once_with(1024)
    message = mock_conn.recv.return_value.decode.return_value
    mock_broadcast.assert_called_once_with(message, mock_clients, 'addr')


def test_del_user_if_recv_invalid_data():
    mock_conn = MagicMock()
    clients = {'addr' : ('conn', 'nickname')}
    mock_conn.recv.return_value = False
    handle_received_data(clients, 'addr', 'nickname', mock_conn)
    assert len(clients) == 0


@mock.patch('server.broadcast')
def test_run_broadcast_if_invalid_data(mock_broadcast):
    mock_conn = MagicMock()
    clients = {'addr' : ('conn', 'nickname')}
    mock_conn.recv.return_value = False
    handle_received_data(clients, 'addr', 'nickname', mock_conn)
    message = 'nickname left from server'
    mock_broadcast.assert_called_once_with(message, clients, 'addr')


@mock.patch('server.get_connection')
def test_broadcast(mock_get_connection):
    mock_conn = MagicMock()
    clients = {'addr': (mock_conn, 'addr')}
    broadcast('message', clients, 'addr')
    mock_conn.send.assert_called_once_with('message'.encode())


@mock.patch('server.Thread')
@mock.patch('server.create_socket')
def test_run_thread_in_main(mock_create_socket, mock_Thread):
    mock_clients = MagicMock()
    main()
    mock_Thread.start.assert_called_once
    mock_Thread.join.assert_called_once

