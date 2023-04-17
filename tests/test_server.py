import pytest
from unittest import mock
from unittest.mock import MagicMock
from server import Server, ServerClient, Event_Type, ClientHandler, MessageHandler, MessageToServer
from queue import Empty
from socket import timeout


@mock.patch('server.Event')
@mock.patch('server.Server.handle_client')
@mock.patch('server.ClientHandler')
@mock.patch('server.Queue')
def test_client_joined_to_server(mock_Queue, mock_ClientHandler,mock_handle_client, mock_Event):
    host = '123'
    port = 123
    server = Server(host, port)
    server_client_mock = MagicMock()
    event = (server_client_mock, Event_Type.ServerClient)
    mock_Queue.return_value.get.side_effect = [event, Empty, KeyboardInterrupt]

    server.start_server()

    mock_ClientHandler.return_value.start.assert_called_once()
    server_client_mock.start.assert_called_once()
    mock_Event.return_value.set.assert_called_once()
    mock_ClientHandler.return_value.join.assert_called_once()


@mock.patch('server.Event')
@mock.patch('server.ClientHandler')
@mock.patch('server.Queue')
@mock.patch('server.Server.handle_message')
def test_get_message_from_client(mock_handle_message, mock_Queue, mock_ClientHandler, mock_Event):
    host = '123'
    port = 123
    server = Server(host, port)
    message_mock = MagicMock()
    event = (message_mock, Event_Type.MessageToServer)
    mock_Queue.return_value.get.side_effect = [event, KeyboardInterrupt]

    server.start_server()

    mock_handle_message.assert_called_once_with(message_mock)
    

@mock.patch('server.MessageToServer')
@mock.patch('server.Server.build_client_left_message')
@mock.patch('server.Server.broadcast')
@mock.patch('server.Server.remove_user')
def test_handle_lef_message(mock_remove_user, mock_broadcast, mock_buid_user_left_message, mock_MessageToServer):
    host = '123'
    port = 123
    server = Server(host, port)
    mock_MessageToServer.message = 'left'
    left_message = 'message'
    mock_buid_user_left_message.return_value = left_message

    server.handle_message(mock_MessageToServer)

    mock_broadcast.assert_called_once_with(left_message, mock_MessageToServer.sender)
    mock_remove_user.assert_called_once_with(mock_MessageToServer)


@mock.patch('server.MessageToServer')
@mock.patch('server.Server.broadcast')
def test_normal_message(mock_broadcast, mock_MessageToServer):
    host = '123'
    port = 123
    server = Server(host, port)
    mock_MessageToServer.message = 'message'

    server.handle_message(mock_MessageToServer)

    mock_broadcast.assert_called_once_with(mock_MessageToServer.message, mock_MessageToServer.sender)


@mock.patch('server.Server.send_server_messages')
def test_remove_user(mock_send_server_messages):
    host = '123'
    port = 123
    server = Server(host, port)
    client = MagicMock()
    client.conn = 'conn'
    client.sender = 'conn'

    server.remove_user(client)
    
    assert server.clients == []


@mock.patch('server.ServerClient')
@mock.patch('server.Message')
def test_send_welcome_message(mock_Message, mock_ServerClient):
    host = '123'
    port = 123
    server = Server(host, port)

    server.send_welcome_message(mock_ServerClient)

    mock_ServerClient.conn.send.assert_called_once_with(mock_Message.return_value.encode.return_value)


@mock.patch('server.Server.broadcast')
@mock.patch('server.ServerClient')
@mock.patch('server.Message')
def test_send_client_join_message(mock_Message, mock_ServerClient, mock_broadcast):
    host = '123'
    port = 123
    server = Server(host, port)

    server.send_message_about_client_join(mock_ServerClient)

    mock_broadcast.assert_called_once_with(mock_Message.return_value.encode.return_value, mock_ServerClient.conn)


@mock.patch('server.ServerClient')
@mock.patch('server.Message')
def test_build_client_left_message(mock_Message, mock_ServerClient):
    host = '123'
    port = 123
    server = Server(host, port)

    message = server.build_client_left_message(mock_ServerClient)

    assert message


def test_broadcast():
    host = '123'
    port = 123
    server = Server(host, port)
    element = MagicMock()
    message = MagicMock()
    element.conn = 'conn'
    conn = 'conn'

    server.broadcast(message, conn)

    element.return_value.conn.send(message)


@mock.patch('server.socket.socket')
def test_create_socket(mock_socket):
    host = '123'
    port = 123
    client_handler = ClientHandler(host, port, 'q', 'event')
    mock_socket.return_value.bind.assert_called_once_with((host, port))    
    mock_socket.return_value.settimeout.assert_called_once_with(1)


@mock.patch('server.Queue')
@mock.patch('server.socket.socket')
def test_accept_client(mock_socket, mock_q):
    host = '123'
    port = 123
    client_handler = ClientHandler(host, port, mock_q, 'event')
    conn = MagicMock()
    addr = MagicMock()
    nickname = 'nickname'
    server_client = ServerClient(conn, addr, nickname, mock_q, 'event')
    mock_socket.return_value.accept.return_value = conn, addr
    conn.recv.return_value.decode.return_value = nickname

    client_handler.accept_client()

    conn.settimeout.assert_called_once_with(1)
    conn.send.assert_called_once_with('nick'.encode())
    mock_q.put.return_value((server_client, Event_Type.ServerClient))


@mock.patch('server.socket.socket')
def test_raise_timeout_exception_in_accept_client(mock_socket):
    host = '123'
    port = 123
    q = MagicMock()
    client_handler = ClientHandler(host, port, q, 'event')
    conn = MagicMock()
    addr = MagicMock()
    mock_socket.return_value.accept.return_value = conn, addr
    conn.send.side_effect = timeout

    client_handler.accept_client()

    conn.settimeout.assert_called_once_with(1)
    q.put.assert_not_called()
    

@mock.patch('server.ClientHandler.accept_client')
@mock.patch('server.socket.socket')
def test_run_client_handler(mock_socket, mock_accept_client):
    host = '123'
    port = 123
    event = MagicMock()
    client_handler = ClientHandler(host, port, 'q', event)
    event.is_set.side_effect = [False, True]

    client_handler.run()

    mock_socket.return_value.listen.assert_called_once()
    mock_accept_client.assert_called_once()


@mock.patch('server.MessageHandler.queue_message')
def test_handle_recv_valid_data(mock_queue_message):
    conn = MagicMock()
    nickname = 'nickname'
    q = 'q'
    event = MagicMock()
    message_handler = MessageHandler(conn, nickname, q, event)
    event.is_set.side_effect = [False, True]
    received_data = 'message'
    conn.recv.return_value = received_data

    message_handler.handle_received_data()

    mock_queue_message.assert_called_once_with(received_data)


def test_no_recv_data():
    conn = MagicMock()
    nickname = 'nickname'
    q = MagicMock()
    event = MagicMock()
    message_handler = MessageHandler(conn, nickname, q, event)
    event.is_set.side_effect = [False]
    conn.recv.return_value = False

    with pytest.raises(Exception) as ex:
        message_handler.handle_received_data()
        assert ex.type is Exception


def test_raise_timeout_exception_in_handle_recv_data():
    conn = MagicMock()
    nickname = 'nickname'
    q = MagicMock()
    event = MagicMock()
    message_handler = MessageHandler(conn, nickname, q, event)
    event.is_set.side_effect = [False, False, True]
    conn.recv.return_value = timeout

    message_handler.handle_received_data()

    assert 2 == conn.recv.call_count


@mock.patch('server.MessageHandler.queue_message')
def test_left_message_recv(mock_queue_message):
    conn = MagicMock()
    nickname = 'nickname'
    q = MagicMock()
    event = MagicMock()
    message_handler = MessageHandler(conn, nickname, q, event)
    event.is_set.side_effect = [False, True]
    received_data = 'left'
    conn.recv.return_value = received_data

    message_handler.handle_received_data()

    mock_queue_message.assert_called_once_with(received_data)


@mock.patch('server.MessageToServer')
def test_put_objects_to_queue(mock_MessageToServer):
    nickname = 'nickname'
    q = MagicMock()
    event = 'event'
    conn = 'conn'
    message_handler = MessageHandler(conn, nickname, q, event)
    message = 'message'

    message_handler.queue_message(message)

    q.put.assert_called_once_with((mock_MessageToServer.return_value, Event_Type.MessageToServer))


@mock.patch('server.MessageHandler.handle_received_data')
def test_run_message_handler(mock_handle_recv_data):
    nickname = 'nickname'
    q = 'q'
    event = 'event'
    conn = MagicMock()
    message_handler = MessageHandler(conn, nickname, q, event)

    message_handler.run()

    mock_handle_recv_data.assert_called_once()
    conn.close.assert_called_once()
