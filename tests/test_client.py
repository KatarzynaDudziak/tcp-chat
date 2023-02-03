import pytest
from unittest import mock
from unittest.mock import MagicMock
from client import Client


@mock.patch('client.socket.socket')
def test_create_client(mock_socket):
    host = '123'
    port = 123
    client = Client(host, port, 'nickname')
    connection = mock_socket.return_value
    connection.connect.assert_called_once_with((host, port))


@mock.patch('client.Thread')
@mock.patch('client.socket.socket')
def test_close_connection_on_exception(mock_socket, mock_Thread):
    host = '123'
    port = 123
    client = Client(host, port, 'nickname')
    mock_Thread.return_value.start.assert_called_once()
    client.connection.recv.return_value.decode.return_value = False
    client.receive_message()
    client.connection.close.assert_called_once()


@mock.patch('client.Thread')
@mock.patch('client.socket.socket')
def test_catch_exception_in_handle_recv_message(mock_socket, mock_Thread):
    host = '123'
    port = 123
    client = Client(host, port, 'nickname')
    client.connection.recv.return_value.decode.return_value = False
    with pytest.raises(Exception) as ex:
        client.handle_recv_message()
    assert ex.type is Exception


@mock.patch('client.Thread')
@mock.patch('client.socket.socket')
def test_handle_nick_message(mock_socket, mock_Thread):
    host = '123'
    port = 123
    client = Client(host, port, 'nickname')
    client.connection.recv.return_value.decode.return_value = 'nick'
    client.handle_recv_message()
    client.connection.send.assert_called_once_with(client.nickname.encode())


@mock.patch('client.Message')
@mock.patch('client.Thread')
@mock.patch('client.socket.socket')
def test_handle_correct_message(mock_socket, mock_Thread, mock_Message):
    host = '123'
    port = 123
    client = Client(host, port, 'nickname')
    receive_callback = MagicMock()
    client.set_callback(receive_callback)
    client.connection.recv.return_value.decode.return_value = 'something'
    client.handle_recv_message()
    mock_Message.return_value.convert_to_obj.assert_called_once_with('something')
    client.receive_callback.assert_called_once_with(mock_Message.return_value)


@mock.patch('client.Thread')
@mock.patch('client.socket.socket')
def test_catch_exception_in_write_message(mock_socket, mock_Thread):
    host = '123'
    port = 123
    client = Client(host, port, 'nickname')
    message = MagicMock()
    message.return_value.encode.side_effect = Exception
    client.write_message(message.return_value)
    client.connection.close.assert_called_once()


@mock.patch('client.Thread')
@mock.patch('client.socket.socket')
def test_send_correct_message_to_server(mock_socket, mock_Thread):
    host = '123'
    port = 123
    client = Client(host, port, 'nickname')
    message = MagicMock()
    message.return_value.encode.return_value = 'something'
    client.write_message(message.return_value)
    client.connection.send.assert_called_once_with('something')


@mock.patch('client.Thread')
@mock.patch('client.socket.socket')
def test_stop_connection(mock_socket, mock_Thread):
    host = '123'
    port = 123
    client = Client(host, port, 'nickname')
    client.stop()
    client.connection.close.assert_called_once()
