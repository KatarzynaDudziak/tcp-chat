import socket
from threading import Thread


class Client:
    connection = None

    def __init__(self, host, port, nickname):
        self.host = host
        self.port = port
        self.create_client()
        self.nickname = nickname
        receive_thread = Thread(target=self.receive_message)
        receive_thread.start()
        self.write_message()

    def create_client(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.port))

    def receive_message(self):
        try:
            while True:
                self.handle_recv_message()
        except Exception as ex:
            print(ex)
            self.connection.close()

    def handle_recv_message(self):
        message = self.connection.recv(1024).decode()
        if not message:
            raise Exception
        if message == 'nick':
            self.connection.send(self.nickname.encode())
        else:
            print(message)

    def write_message(self):
        try:
            while True:
                self.send_message_to_server()
        except:
            print('Cannot send message')
            self.connection.close()    

    def send_message_to_server(self):
        message = f'{self.nickname}: {input()}'
        self.connection.send(message.encode())


def main():
    nickname = input("Write your nickname: ")
    client = Client('127.0.0.1', 3888, nickname)

if __name__ == "__main__":
    main()
