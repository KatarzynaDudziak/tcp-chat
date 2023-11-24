import pytest
from unittest.mock import call, MagicMock
from client import *


class TestClient:

    @pytest.fixture
    def setup_client(self, mocker):
        self.host ='123'
        self.port = 123
        self.q  = MagicMock()
        self.conn = MagicMock()
        self.mock_socket = mocker.patch('client.socket')
        self.mock_event = mocker.patch('client.Event')
        self.mock_message_handler = mocker.patch('client.MessageHandler')
        self.mock_socket.socket.return_value = self.conn
        self.client = Client(self.host, self.port, 'nickname', self.q)
        yield

    def test_should_create_socket(self, setup_client):
        self.mock_socket.socket.assert_called_once_with(self.mock_socket.AF_INET, self.mock_socket.SOCK_STREAM)
        self.mock_socket.socket.return_value.settimeout.assert_called_once()
        self.mock_socket.socket.return_value.connect.assert_called_once_with((self.host, self.port))

    def test_should_send_encoded_message(self, setup_client):
        message = MagicMock()

        self.client.write_message(message)

        self.client.conn.send.assert_called_once_with(message.encode.return_value)

    def test_should_close_connection(self, setup_client):
        self.client.stop()

        self.mock_event.return_value.set.assert_called_once()
        self.mock_message_handler.return_value.join.assert_called_once()
        self.conn.close.assert_called_once()


class TestMessageHandler:

    @pytest.fixture
    def setup_message_handler(self, mocker):
        self.conn = MagicMock()
        self.q = MagicMock()
        self.nickname = MagicMock()
        self.event = MagicMock()
        self.mock_get_message = mocker.patch('client.get_message')
        self.mock_message = mocker.patch('client.Message')
        self.mock_event = mocker.patch('client.Event')
        self.mock_thread = mocker.patch('client.Thread')
        yield

    def test_should_put_received_message_on_queue(self, setup_message_handler):
        self.mock_get_message.return_value = 'messsage'
        self.event.is_set.side_effect = [False, True]
        message_handler = MessageHandler(self.conn, self.q, self.nickname, self.event)

        message_handler.run()

        self.q.put.assert_called_once_with(self.mock_message.return_value)

    def test_should_send_received_nick_message(self, setup_message_handler):
        self.mock_get_message.return_value = 'nick'
        self.event.is_set.side_effect = [False, True]
        message_handler = MessageHandler(self.conn, self.q, self.nickname, self.event)

        message_handler.run()

        self.conn.send.assert_called_once_with(self.nickname.encode.return_value)
        self.conn.close.assert_called_once()

    def test_should_back_to_while_loop_when_no_message(self, setup_message_handler):
        self.mock_get_message.return_value = None
        expected_calls = [(call(), call())]
        message_handler = MessageHandler(self.conn, self.q, self.nickname, self.event)
        self.event.is_set.side_effect = [False, True]

        message_handler.run()

        self.q.put.assert_not_called()
        self.event.is_set.assert_has_calls(expected_calls)

    def test_should_catch_errors_after_disconnected(self, setup_message_handler):
        self.mock_get_message.side_effect = [ConnectionAbortedError, TimeoutError]
        message_handler = MessageHandler(self.conn, self.q, self.nickname, self.event)
        self.event.is_set.side_effect = [False, False, True]

        message_handler.run()
        
        self.q.put.assert_called_once_with(self.mock_message.return_value)


def test_should_receive_and_decode_message(mocker):
    conn = MagicMock()
    recv_message_mock = MagicMock()
    mock_struct = mocker.patch('client.struct')
    conn.recv.side_effect = ['12', recv_message_mock]
    calls = [call(4), call(mock_struct.unpack.return_value.__getitem__.return_value)]

    recv_message = get_message(conn)

    conn.recv.assert_has_calls(calls)
    mock_struct.unpack.assert_called_once_with('!I', '12')
    mock_struct.unpack.return_value.__getitem__.assert_called_once_with(0)
    assert recv_message == recv_message_mock.decode.return_value
    

def test_should_raise_connection_aborted_error_when_empty_header():
    conn = MagicMock()
    conn.recv.return_value = b''

    with pytest.raises(Exception) as ex:
        get_message(conn)
    
    assert ex.type == ConnectionAbortedError
