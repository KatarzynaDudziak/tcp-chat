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
def test_client_joined_to_server(mock_queue, mock_client_handler, mock_event):
    host = '123'
    port = 123
    server = Server(host, port)
    server_client_mock = MagicMock()
    event = (server_client_mock, EventType.ServerClient)
    mock_queue.return_value.get.side_effect = [event, Empty, KeyboardInterrupt]

    server.start_server()

    mock_client_handler.return_value.start.assert_called_once()
    server_client_mock.start.assert_called_once()
    mock_event.return_value.set.assert_called_once()
    mock_client_handler.return_value.join.assert_called_once()


@mock.patch('server.Builder')
@mock.patch('server.Event')
@mock.patch('server.ClientHandler')
@mock.patch('server.Queue')
def test_should_send_messages_to_client_when_client_join(mock_queue, mock_client_handler, mock_event, mock_builder):
    host = '123'
    port = 123
    server = Server(host, port)
    server_client_mock = MagicMock()
    server_client_mock_2 = MagicMock()
    server_client_mock_2.conn = MagicMock()
    message_mock = MagicMock()
    message_mock.sender = server_client_mock_2.conn
    calls = [call(mock_builder.return_value.build_welcome_message.return_value),
            call(mock_builder.return_value.build_message_about_client_join.return_value),
            call(message_mock.message)]
    event_client = (server_client_mock, EventType.ServerClient)
    event_client_2 = (server_client_mock_2, EventType.ServerClient)
    event_message = (message_mock, EventType.MessageToServer)
    mock_queue.return_value.get.side_effect = [event_client, event_client_2, event_message, KeyboardInterrupt]

    server.start_server()

    server_client_mock.conn.send.assert_has_calls(calls)


@mock.patch('server.Builder')
@mock.patch('server.Event')
@mock.patch('server.ClientHandler')
@mock.patch('server.Queue')
def test_should_remove_client_from_clients_list_when_client_left(mock_queue, mock_client_handler, mock_event, mock_builder):
    host = '123'
    port = 123
    server = Server(host, port)
    server_client_mock = MagicMock()
    server_client_mock_2 = MagicMock()
    server_client_mock_2.conn = MagicMock()
    message_mock = MagicMock()
    message_mock.message = 'left'
    message_mock.sender = server_client_mock_2.conn
    calls = [call(mock_builder.return_value.build_client_left_message.return_value)]
    event_client = (server_client_mock, EventType.ServerClient)
    event_client_2 = (server_client_mock_2, EventType.ServerClient)
    event_client_left = (message_mock, EventType.MessageToServer)
    mock_queue.return_value.get.side_effect = [event_client, event_client_2, event_client_left, KeyboardInterrupt]

    server.start_server()

    server_client_mock.conn.send.assert_has_calls(calls)
    assert len(server.clients) == 1


@mock.patch('server.Queue')
@mock.patch('server.ServerClient')
@mock.patch('server.Thread')
@mock.patch('server.socket.socket')
def test_create_socket(mock_socket, mock_thread, mock_server_client, mock_queue):
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
def test_should_put_client_on_clients_list(mock_socket, mock_thread, mock_server_client, mock_message):
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
    q.put.assert_called_once_with((mock_server_client.return_value, EventType.ServerClient))


@mock.patch('server.ServerClient')
@mock.patch('server.Thread')
@mock.patch('server.socket.socket')
def test_should_back_to_while_loop_when_timeout_occurs(mock_socket, mock_thread, mock_server_client):
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
def test_should_raise_value_error_when_decode_gets_incorrect_data(mock_socket, mock_thread, mock_server_client, mock_message):
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

   
@mock.patch('server.Thread')
@mock.patch('server.MessageToServer')
def test_put_message_on_queue_after_recv_data(mock_message_to_server, mock_thread):
    conn = MagicMock()
    nickname = 'nickname'
    q = MagicMock()
    event = MagicMock()
    message_handler = MessageHandler(conn, nickname, q, event)
    event.is_set.side_effect = [False, True]

    message_handler.run()

    mock_message_to_server.assert_called_once_with(conn.recv.return_value, conn, nickname)
    q.put.assert_called_once_with((mock_message_to_server.return_value, EventType.MessageToServer))
    conn.close.assert_called_once()


@mock.patch('server.Thread')
@mock.patch('server.MessageToServer')
def test_should_trigger_remove_client_when_no_recv_data(mock_message_to_server, mock_thread):
    conn = MagicMock()
    nickname = 'nickname'
    q = MagicMock()
    event = MagicMock()
    message_handler = MessageHandler(conn, nickname, q, event)
    conn.recv.return_value = None
    event.is_set.side_effect = [False, True]

    message_handler.run()

    mock_message_to_server.assert_called_once_with('left', conn, nickname)
    q.put.assert_called_once_with((mock_message_to_server.return_value, EventType.MessageToServer))
    event.is_set.assert_called_once()


@mock.patch('server.Thread')
def test_should_repeat_loop_when_recv_throws_timeout(mock_thread):
    conn = MagicMock()
    nickname = 'nickname'
    q = MagicMock()
    event = MagicMock()
    expected_calls = [call(), call()]
    conn.recv.side_effect = [TimeoutError]
    event.is_set.side_effect = [False, True]
    message_handler = MessageHandler(conn, nickname, q, event)

    message_handler.run()

    event.is_set.assert_has_calls(expected_calls)


@mock.patch('server.Thread')
@mock.patch('server.MessageToServer')
def test_should_trigger_remove_client_on_conncection_reset_error(mock_message_to_server, mock_thread):
    conn = MagicMock()
    nickname = 'nickname'
    q = MagicMock()
    event = MagicMock()
    conn.recv.side_effect = [ConnectionResetError]
    event.is_set.side_effect = [False]
    message_handler = MessageHandler(conn, nickname, q, event)

    message_handler.run()

    mock_message_to_server.assert_called_once_with('left', conn, nickname)
    q.put.assert_called_once_with((mock_message_to_server.return_value, EventType.MessageToServer))
    event.is_set.assert_called_once()
