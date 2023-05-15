from unittest import mock
from unittest.mock import MagicMock
from console_app import *


def test_receive_callback_message():
    message = MagicMock()
    message.publication_date = '22.03.1999'
    message.author = 'Tester'
    message.message = 'message'

    receive_callback_message(message)
    
    given = f'{message.publication_date} {message.author} {message.message}'
    expected = '22.03.1999 Tester message'
    assert expected == given

@mock.patch('console_app.Message')
@mock.patch('console_app.Client')
@mock.patch('console_app.input')
def test_keyboardInterrupt_main(mock_input, mock_Client, mock_Message):
    mock_Client.return_value.write_message.side_effect = [KeyboardInterrupt]

    main()

    mock_Message.assert_called_once()
    assert 2 == mock_input.call_count
    mock_Client.return_value.write_message.assert_called_once()
    mock_Client.return_value.stop.assert_called_once()


@mock.patch('console_app.Message')
@mock.patch('console_app.Client')
@mock.patch('console_app.input')
def test_write_few_messages(mock_input, mock_Client, mock_Message):
    mock_input.side_effect = ['nickname', 'new', 'eee', KeyboardInterrupt]

    main()
    
    assert 3 == mock_Message.call_count
    assert 4 == mock_input.call_count
    assert 2 == mock_Client.return_value.write_message.call_count
