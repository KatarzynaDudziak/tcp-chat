from client import Client
from message import Message


def receive_callback_message(message):
    print(f'{message.publication_date} {message.author} {message.message}')


def main():
    nickname = input("Write your nickname: ")
    client = Client('127.0.0.1', 3889, nickname, receive_callback_message)
    while True:
        try:
            message = Message()
            message.message = input()
            message.author = nickname
            client.write_message(message)
        except KeyboardInterrupt:
            client.stop()
            break

if __name__ == "__main__":
    main()
