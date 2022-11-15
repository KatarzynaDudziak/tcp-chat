import pytest
from unittest import mock
from unittest.mock import MagicMock
from server import *


@pytest.fixture
def host():
    host = '123'
    return host


@pytest.fixture
def port():
    port = 123
    return port


@pytest.fixture
def socket():
    socket = MagicMock()
    return socket


@pytest.fixture
def clients():
    clients = MagicMock()
    return clients


@pytest.fixture
def clients_dict():
    clients = {'addr' : ('conn', 'nickname')}
    return clients


@pytest.fixture
def clients_empty_dict():
    clients = dict()
    return clients


@pytest.fixture
def conn():
    conn = MagicMock()
    return conn


@mock.patch('server.socket.socket')
def test_create_socket(mock_socket, host, port):
    s = create_socket(host, port)
    assert s == mock_socket.return_value


@mock.patch('server.socket.socket')
def test_socket_bind(mock_socket, host, port):
    create_socket(host, port)
    mock_socket.return_value.bind.assert_called_once_with((host, port))


@mock.patch('server.socket.socket')
def test_socket_listen(mock_socket, host, port):
    create_socket(host, port)
    mock_socket.return_value.listen.assert_called_once()


@mock.patch('server.Thread')
@mock.patch('server.accept_client')
def test_handle_one_client(mock_accept_client, mock_Thread, socket, clients):
    handle_one_client(socket, clients)
    mock_accept_client.assert_called_once_with(socket, clients)
    mock_Thread.return_value.start.assert_called_once()


def test_socket_accept(socket, clients, conn):
    socket.accept.return_value = (conn, 'addr')
    accept_client(socket, clients)
    socket.accept.assert_called_once()


def test_send_nick_message(socket, clients, conn):
    socket.accept.return_value = (conn, 'addr')
    accept_client(socket, clients)
    conn.send.assert_called_once_with('nick'.encode())


def test_recv_and_decoding_nickname(socket, clients, conn):
    socket.accept.return_value = (conn, 'addr')
    accept_client(socket, clients)
    conn.recv.assert_called_once_with(1024)
    conn.recv.return_value.decode.assert_called_once()


def test_adding_client_with_nickname(socket, conn, clients_empty_dict):
    socket.accept.return_value = (conn, 'addr')
    conn.recv.return_value.decode.return_value = 'nick'
    accept_client(socket, clients_empty_dict)
    assert clients_empty_dict['addr'] == (conn, 'nick')


def test_returning_addr(socket, conn, clients_dict):
    socket.accept.return_value = (conn, 'addr')
    assert accept_client(socket, clients_dict) == 'addr'


@mock.patch('server.get_connection')
@mock.patch('server.get_nickname')
def test_send_server_message(mock_get_nickname, mock_get_connection, clients):
    addr = 'addr'
    mock_get_nickname.return_value = 'nick'
    send_server_messages_on_client_join(clients, addr)
    message = 'Hello nick from server to client'
    mock_get_connection.return_value.send.assert_called_once_with(message.encode())


def test_returning_nickname(clients_dict):
    assert get_nickname(clients_dict, 'addr') == 'nickname'


def test_no_nickname_in_clients():
    clients = {'addr' : 'conn'}
    with pytest.raises(KeyError):
        get_nickname(clients, 'addr2')


def test_returning_connection(clients_dict):
    assert get_connection(clients_dict, 'addr') == 'conn'


def test_no_connection_in_clients():
    clients = {'addr' : 'nickname'}
    with pytest.raises(KeyError):
        get_connection(clients, 'addr2')


@mock.patch('server.handle_messages_for_client')
def test_no_handle_messages_for_no_clients(mock_handle_messages_for_client, clients_empty_dict):
    handle_messages(clients_empty_dict, 'addr')
    mock_handle_messages_for_client.assert_not_called()


@mock.patch('server.handle_messages_for_client')
def test_handle_messages_one_client(mock_handle_messages_for_client, clients):
    clients.__contains__.side_effect = [True, False]
    handle_messages(clients, 'addr')
    mock_handle_messages_for_client.assert_called_once()


@mock.patch('server.handle_received_data')
@mock.patch('server.get_connection')
@mock.patch('server.get_nickname')
def test_handle_messages_for_client(mock_get_nickname, mock_get_connection, mock_handle_received_data, clients):
    mock_get_nickname.return_value = 'nickname'
    mock_get_connection.return_value = 'conn'
    handle_messages_for_client(clients, 'addr')
    mock_get_nickname.assert_called_once_with(clients, 'addr')
    mock_get_connection.assert_called_once_with(clients, 'addr')
    mock_handle_received_data.assert_called_once_with(clients, 'addr', 'nickname', 'conn')


def test_recv_valid_data(clients, conn):
    handle_received_data(clients, 'addr', 'nickname', conn)
    conn.recv.assert_called_once_with(1024)
    conn.recv.return_value.decode.assert_called_once()


@mock.patch('server.broadcast')
def test_run_broadcast_if_valid_data(mock_broadcast, clients, conn):
    conn.recv.return_value.decode.return_value = 'message'
    handle_received_data(clients, 'addr', 'nickname', conn)
    conn.recv.assert_called_once_with(1024)
    mock_broadcast.assert_called_once_with('message', clients, 'addr')


def test_del_user_if_recv_invalid_data(conn, clients_dict):
    conn.recv.return_value = False
    handle_received_data(clients_dict, 'addr', 'nickname', conn)
    assert len(clients_dict) == 0


@mock.patch('server.broadcast')
def test_run_broadcast_if_invalid_data(mock_broadcast, conn, clients_dict):
    conn.recv.return_value = False
    handle_received_data(clients_dict, 'addr', 'nickname', conn)
    message = 'nickname left from server'
    mock_broadcast.assert_called_once_with(message, clients_dict, 'addr')


@mock.patch('server.get_connection')
def test_broadcast(mock_get_connection, conn):
    clients = {'addr': (conn, 'addr')}
    broadcast('message', clients, 'addr')
    conn.send.assert_called_once_with('message'.encode())


@mock.patch('server.Thread')
@mock.patch('server.create_socket')
def test_run_thread_in_main(mock_create_socket, mock_Thread, clients):
    main()
    mock_Thread.return_value.start.assert_called_once()
    mock_Thread.return_value.join.assert_called_once()
