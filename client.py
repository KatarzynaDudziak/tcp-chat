import socket
from threading import Thread
from datetime import datetime
from message import Message


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
        except Exception as ex:
            print(ex)
            self.connection.close()

    def handle_recv_message(self):
        recv_message = self.connection.recv(1024).decode()
        if not recv_message:
            raise Exception
        if recv_message == 'nick':
            self.connection.send(self.nickname.encode())
        else:
            message = Message()
            message.convert_to_obj(recv_message)
            if self.receive_callback:
                self.receive_callback(message)

    def write_message(self, message):
        try:
            self.send_message_to_server(message)
        except Exception as ex:
            self.connection.close()

    def send_message_to_server(self, message):
        message_to_send = message.encode()
        self.connection.send(message_to_send)

    def stop(self):
        self.connection.close()
