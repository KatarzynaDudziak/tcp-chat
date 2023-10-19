import pytest
from unittest import mock
from unittest.mock import MagicMock
from client import Client


@mock.patch('client.socket')
@mock.patch('client.Event')
@mock.patch('client.Thread')
def test_create_socket(mock_thread, mock_event, mock_socket):
    host = '123'
    port = 123
    q  = MagicMock()
    client = Client(host, port, 'nickname', q)

    mock_socket.socket.assert_called_once_with(mock_socket.AF_INET, mock_socket.SOCK_STREAM)
    mock_socket.socket.return_value.settimeout.assert_called_once()
    mock_socket.socket.return_value.connect.assert_called_once_with((host, port))

