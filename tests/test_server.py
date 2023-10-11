import pytest
from unittest import mock
from unittest.mock import call, MagicMock
from server import Server, ServerClient, EventType, ClientHandler, MessageHandler
from message import Message
from queue import Empty
from socket import timeout


@mock.patch('server.Event')
@mock.patch('server.ClientHandler')
@mock.patch('server.Queue')
def test_client_joined_to_server(mock_Queue, mock_ClientHandler, mock_Event):
    host = '123'
    port = 123
    server = Server(host, port)
    server_client_mock = MagicMock()
    event = (server_client_mock, EventType.ServerClient)
    mock_Queue.return_value.get.side_effect = [event, Empty, KeyboardInterrupt]

    server.start_server()

    mock_ClientHandler.return_value.start.assert_called_once()
    server_client_mock.start.assert_called_once()
    mock_Event.return_value.set.assert_called_once()
    mock_ClientHandler.return_value.join.assert_called_once()


@mock.patch('server.Builder')
@mock.patch('server.Event')
@mock.patch('server.ClientHandler')
@mock.patch('server.Queue')
def test_send_messages_to_client(mock_Queue, mock_ClientHandler, mock_Event, mock_Builder):
    host = '123'
    port = 123
    server = Server(host, port)
    server_client_mock = MagicMock()
    server_client_mock_2 = MagicMock()
    server_client_mock_2.conn = MagicMock()
    message_mock = MagicMock()
    message_mock.sender = server_client_mock_2.conn
    calls = [call(mock_Builder.return_value.build_welcome_message.return_value),
            call(mock_Builder.return_value.build_message_about_client_join.return_value),
            call(message_mock.message)]
    event_client = (server_client_mock, EventType.ServerClient)
    event_client_2 = (server_client_mock_2, EventType.ServerClient)
    event_message = (message_mock, EventType.MessageToServer)
    mock_Queue.return_value.get.side_effect = [event_client, event_client_2, event_message, KeyboardInterrupt]

    server.start_server()

    server_client_mock.conn.send.assert_has_calls(calls)


@mock.patch('server.Builder')
@mock.patch('server.Event')
@mock.patch('server.ClientHandler')
@mock.patch('server.Queue')
def test_remove_client_from_clients_list(mock_Queue, mock_ClientHandler, mock_Event, mock_Builder):
    host = '123'
    port = 123
    server = Server(host, port)
    server_client_mock = MagicMock()
    server_client_mock_2 = MagicMock()
    server_client_mock_2.conn = MagicMock()
    message_mock = MagicMock()
    message_mock.message = 'left'
    message_mock.sender = server_client_mock_2.conn
    calls = [call(mock_Builder.return_value.build_client_left_message.return_value)]
    event_client = (server_client_mock, EventType.ServerClient)
    event_client_2 = (server_client_mock_2, EventType.ServerClient)
    event_client_left = (message_mock, EventType.MessageToServer)
    mock_Queue.return_value.get.side_effect = [event_client, event_client_2, event_client_left, KeyboardInterrupt]

    server.start_server()

    server_client_mock.conn.send.assert_has_calls(calls)
    assert len(server.clients) == 1


@mock.patch('server.Queue')
@mock.patch('server.ServerClient')
@mock.patch('server.Thread')
@mock.patch('server.socket.socket')
def test_create_socket(mock_socket, mock_thread, mock_ServerClient, mock_queue):
    host = '123'
    port = 123
    q = mock_queue
    event = 'event'

    ClientHandler(host, port, q, event)

    mock_socket.return_value.bind.assert_called_once_with((host, port))
    mock_socket.return_value.settimeout.assert_called_once_with(1)


@mock.patch('server.Message')
@mock.patch('server.ServerClient')
@mock.patch('server.Thread')
@mock.patch('server.socket.socket')
def test_accept_client(mock_socket, mock_thread, mock_ServerClient, mock_message):
    host = '123'
    port = 123
    q = MagicMock()
    event = MagicMock()
    client_handler = ClientHandler(host, port, q, event)
    conn = MagicMock()
    addr = 'addr'
    nickname = 'nickname'
    mock_socket.return_value.accept.return_value = conn, addr
    conn.recv.return_value.decode.return_value = nickname
    event.is_set.side_effect = [False, True]
    
    client_handler.run()

    conn.send.assert_called_once_with(mock_message.return_value.encode_nickname.return_value)
    q.put.assert_called_once_with((mock_ServerClient.return_value, EventType.ServerClient))


@mock.patch('server.ServerClient')
@mock.patch('server.Thread')
@mock.patch('server.socket.socket')
def test_raise_exception_on_accept_client(mock_socket, mock_thread, mock_ServerClient):
    host = '123'
    port = 123
    q = MagicMock()
    event = MagicMock()
    message = MagicMock()
    client_handler = ClientHandler(host, port, q, event)
    mock_socket.return_value.accept.side_effect = [timeout]
    event.is_set.side_effect = [False, True]
    
    client_handler.run()

    message.return_value.assert_not_called()


@mock.patch('server.Message')
@mock.patch('server.ServerClient')
@mock.patch('server.Thread')
@mock.patch('server.socket.socket')
def test_check_if_UnicodeDecodeError_occurs(mock_socket, mock_thread, mock_ServerClient, mock_message):
    host = '123'
    port = 123
    q = MagicMock()
    event = MagicMock()
    conn = MagicMock()
    addr = 'addr'
    client_handler = ClientHandler(host, port, q, event)
    mock_socket.return_value.accept.return_value = conn, addr
    conn.recv.return_value.decode.side_effect = [ValueError]
    event.is_set.side_effect = [False]

    with pytest.raises(ValueError):
        client_handler.run()
    
    q.return_value.put.assert_not_called()
    
