import pytest
from unittest import mock
from unittest.mock import MagicMock
from server import Server, ServerClient, Event_Type
from queue import Empty


@mock.patch('server.Event')
@mock.patch('server.ClientHandler')
@mock.patch('server.Queue')
def test_client_joined_to_server(mock_Queue, mock_ClientHandler, mock_Event):
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
    server.handle_client(client)
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
