import pytest
from unittest import mock
from unittest.mock import MagicMock
from client import *

@mock.patch('client.socket.socket')
def test_create_client(mock_socket):
    host = '123'
    port = 123
    client = create_client(host, port)
    assert client == mock_socket.return_value

