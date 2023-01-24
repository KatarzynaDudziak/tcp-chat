import socket
from threading import Thread


class Client:
    connection = None

    def __init__(self, host, port, nickname):
        self.host = host
        self.port = port
        self.create_client()
        self.nickname = nickname
        self.receive_callback = None

        self.receive_thread = Thread(target=self.receive_message)
        self.receive_thread.start()

    def create_client(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.port))

    def set_callback(self, callback):
        self.receive_callback = callback

    def receive_message(self):
        try:
            while True:
                self.handle_recv_message()
        except Exception:
            self.connection.close()

    def handle_recv_message(self):
        recv_message = self.connection.recv(1024).decode()
        if not recv_message:
            raise Exception
        if recv_message == 'nick':
            self.connection.send(self.nickname.encode())
        else:
            if self.receive_callback:
                self.receive_callback(recv_message)

    def write_message(self, message):
        try:
            self.__send_message_to_server(message)
        except:
            self.connection.close()

    def __send_message_to_server(self, message):
        message_to_send = f'{self.nickname}: {message}'
        self.connection.send(message_to_send.encode())

    def stop(self):
        self.connection.close()
