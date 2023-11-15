import pytest
from unittest.mock import call, MagicMock
from server import Server, ServerClient, EventType, ClientHandler, MessageHandler
from message import Message
from queue import Empty
from socket import timeout


class TestServer:

    @pytest.fixture
    def setup_server(self, mocker):
        self.host = '123'
        self.port = 123
        self.server_client_mock = MagicMock()
        self.mock_queue = mocker.patch('server.Queue')
        self.mock_builder = mocker.patch('server.Builder')
        self.mock_event = mocker.patch('server.Event')
        self.mock_client_handler = mocker.patch('server.ClientHandler')
        self.server = Server(self.host, self.port)
        yield

    def test_client_joined_to_server(self, setup_server):
        event = (self.server_client_mock, EventType.ServerClient)
        self.mock_queue.return_value.get.side_effect = [event, Empty, KeyboardInterrupt]

        self.server.start_server()

        self.mock_client_handler.return_value.start.assert_called_once()
        self.server_client_mock.start.assert_called_once()
        self.mock_event.return_value.set.assert_called_once()
        self.mock_client_handler.return_value.join.assert_called_once()
  
    def test_should_send_messages_to_client_when_client_join(self, setup_server):
        server_client_mock_2 = MagicMock()
        server_client_mock_2.conn = MagicMock()
        message_mock = MagicMock()
        message_mock.sender = server_client_mock_2.conn
        calls = [call(self.mock_builder.return_value.build_welcome_message.return_value),
                call(self.mock_builder.return_value.build_message_about_client_join.return_value),
                call(message_mock.message)]
        event_client = (self.server_client_mock, EventType.ServerClient)
        event_client_2 = (server_client_mock_2, EventType.ServerClient)
        event_message = (message_mock, EventType.MessageToServer)
        self.mock_queue.return_value.get.side_effect = [event_client, event_client_2, event_message, KeyboardInterrupt]

        self.server.start_server()

        self.server_client_mock.conn.send.assert_has_calls(calls)

    def test_should_remove_client_from_clients_list_when_client_left(self, setup_server):
        server_client_mock_2 = MagicMock()
        server_client_mock_2.conn = MagicMock()
        message_mock = MagicMock()
        message_mock.message = 'left'
        message_mock.sender = server_client_mock_2.conn
        calls = [call(self.mock_builder.return_value.build_client_left_message.return_value)]
        event_client = (self.server_client_mock, EventType.ServerClient)
        event_client_2 = (server_client_mock_2, EventType.ServerClient)
        event_client_left = (message_mock, EventType.MessageToServer)
        self.mock_queue.return_value.get.side_effect = [event_client, event_client_2, event_client_left, KeyboardInterrupt]

        self.server.start_server()

        self.server_client_mock.conn.send.assert_has_calls(calls)
        assert len(self.server.clients) == 1


class TestClientHandler:

    @pytest.fixture
    def setup_client_handler(self, mocker):
        self.host = '123'
        self.port = 123
        self.q = MagicMock()
        self.event = MagicMock()
        self.mock_socket = mocker.patch('server.socket.socket')
        self.mock_thread = mocker.patch('server.Thread')
        self.mock_server_client = mocker.patch('server.ServerClient')
        self.mock_queue = mocker.patch('server.Queue')
        self.mock_message = mocker.patch('server.Message')
        self.client_handler = ClientHandler(self.host, self.port, self.q, self.event)
        yield

    def test_create_socket(self, setup_client_handler):
        self.mock_socket.return_value.bind.assert_called_once_with((self.host, self.port))
        self.mock_socket.return_value.settimeout.assert_called_once_with(1)

    def test_should_put_client_on_clients_list(self, setup_client_handler):
        conn = MagicMock()
        addr = 'addr'
        nickname = 'nickname'
        self.mock_socket.return_value.accept.return_value = conn, addr
        conn.recv.return_value.decode.return_value = nickname
        self.event.is_set.side_effect = [False, True]
        
        self.client_handler.run()

        conn.send.assert_called_once_with(self.mock_message.return_value.encode_nickname.return_value)
        self.q.put.assert_called_once_with((self.mock_server_client.return_value, EventType.ServerClient))

    def test_should_back_to_while_loop_when_timeout_occurs(self, setup_client_handler):
        message = MagicMock()
        self.mock_socket.return_value.accept.side_effect = [timeout]
        self.event.is_set.side_effect = [False, True]
        
        self.client_handler.run()

        message.return_value.assert_not_called()

    def test_should_raise_value_error_when_decode_gets_incorrect_data(self, setup_client_handler):
        conn = MagicMock()
        addr = 'addr'
        self.mock_socket.return_value.accept.return_value = conn, addr
        conn.recv.return_value.decode.side_effect = [ValueError]
        self.event.is_set.side_effect = [False]

        with pytest.raises(ValueError):
            self.client_handler.run()
        
        self.q.return_value.put.assert_not_called()


class TestMessageHandler:
    
    @pytest.fixture
    def setup_message_handler(self, mocker):
        self.conn = MagicMock()
        self.nickname = 'nickname'
        self.q = MagicMock()
        self.event = MagicMock()
        self.mock_thread = mocker.patch('server.Thread')
        self.mock_message_to_server = mocker.patch('server.MessageToServer')
        self.message_handler = MessageHandler(self.conn, self.nickname, self.q, self.event)
        yield
   
    def test_put_message_on_queue_after_recv_data(self, setup_message_handler):
        self.event.is_set.side_effect = [False, True]

        self.message_handler.run()

        self.mock_message_to_server.assert_called_once_with(self.conn.recv.return_value, self.conn, self.nickname)
        self.q.put.assert_called_once_with((self.mock_message_to_server.return_value, EventType.MessageToServer))
        self.conn.close.assert_called_once()

    def test_should_trigger_remove_client_when_no_recv_data(self, setup_message_handler):
        self.conn.recv.return_value = None
        self.event.is_set.side_effect = [False, True]

        self.message_handler.run()

        self.mock_message_to_server.assert_called_once_with('left', self.conn, self.nickname)
        self.q.put.assert_called_once_with((self.mock_message_to_server.return_value, EventType.MessageToServer))
        self.event.is_set.assert_called_once()

    def test_should_repeat_loop_when_recv_throws_timeout(self, setup_message_handler):
        expected_calls = [call(), call()]
        self.conn.recv.side_effect = [TimeoutError]
        self.event.is_set.side_effect = [False, True]

        self.message_handler.run()

        self.event.is_set.assert_has_calls(expected_calls)

    def test_should_trigger_remove_client_on_conncection_reset_error(self, setup_message_handler):
        self.conn.recv.side_effect = [ConnectionResetError]
        self.event.is_set.side_effect = [False]

        self.message_handler.run()

        self.mock_message_to_server.assert_called_once_with('left', self.conn, self.nickname)
        self.q.put.assert_called_once_with((self.mock_message_to_server.return_value, EventType.MessageToServer))
        self.event.is_set.assert_called_once()
